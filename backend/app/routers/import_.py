from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import TokenPayload, verify_api_key, verify_jwt
from app.models import CSAT, Ad, Agent, Channel, ClosedConversation, Contact, Lifecycle, Team
from app.schemas.import_ import ImportResponse, ImportTemplateResponse, SpreadsheetType

router = APIRouter(prefix="/api/import", tags=["import"])


def get_or_create_channel(db: Session, channel_id: int, name: str | None = None) -> int:
    existing = db.query(Channel).filter(Channel.channel_id == channel_id).first()
    if existing:
        return existing.id
    new_channel = Channel(channel_id=channel_id, name=name or f"Canal {channel_id}")
    db.add(new_channel)
    db.flush()
    return new_channel.id


def get_or_create_agent(db: Session, agent_id: int | None, name: str | None = None, agent_type: str = "user") -> int:
    if agent_id is not None:
        existing = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if existing:
            return existing.id
    else:
        if name:
            existing = db.query(Agent).filter(Agent.name == name).first()
            if existing:
                return existing.id
        else:
            return 0

    if agent_id is None and name:
        import hashlib

        agent_id = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

    new_agent = Agent(agent_id=agent_id, name=name or f"Agente {agent_id}", agent_type=agent_type)
    db.add(new_agent)
    db.flush()
    return new_agent.id


def get_or_create_team(db: Session, team_id: int, name: str | None = None) -> int:
    existing = db.query(Team).filter(Team.team_id == team_id).first()
    if existing:
        return existing.id
    new_team = Team(team_id=team_id, name=name or f"Equipo {team_id}")
    db.add(new_team)
    db.flush()
    return new_team.id


def get_or_create_contact(
    db: Session, contact_id: int, nombre: str | None = None, email: str | None = None, telefono: str | None = None
) -> int:
    existing = db.query(Contact).filter(Contact.contact_id == contact_id).first()
    if existing:
        if nombre and not existing.nombre:
            existing.nombre = nombre
        if email and not existing.email:
            existing.email = email
        if telefono and not existing.telefono:
            existing.telefono = telefono
        db.flush()
        return existing.id
    new_contact = Contact(
        contact_id=contact_id,
        nombre=nombre,
        email=email,
        telefono=telefono,
    )
    db.add(new_contact)
    db.flush()
    return new_contact.id


COLUMN_MAPPING = {
    SpreadsheetType.CLOSED_CONVERSATIONS: {
        "Fecha": "fecha",
        "Canal": "canal_id",
        "Cesionario": "cesionario_id",
        "Equipo": "equipo_id",
        "Tipificacion": "tipificacion",
        "Resumen": "resumen",
    },
    SpreadsheetType.LIFECYCLES: {
        "Fecha": "fecha",
        "Ciclo de vida": "ciclo_vida",
        "PAis": "pais",
        "Cesionario": "cesionario_id",
        "Vendedor": "vendedor",
        "Canal": "canal",
    },
    SpreadsheetType.ADS: {
        "Agente": "agente_id",
        "Contact ID": "contact_id",
        "{{$clicktochat.ad_timestamp}} ": "ad_timestamp",
        "{{$clicktochat.ad_channel_id}}": "ad_channel_id",
        "{{$clicktochat.ad_channel_type}}": "ad_channel_type",
        "{{$clicktochat.ad_contact_type}}": "ad_contact_type",
        "{{$clicktochat.ad_adset_id}}": "ad_adset_id",
        "{{$clicktochat.ad_adset_name}}": "ad_adset_name",
        "{{$clicktochat.ad_ad_url}}": "ad_ad_url",
        "{{$clicktochat.ad_status}}": "ad_status",
    },
    SpreadsheetType.CSAT: {
        "Fecha": "fecha",
        "ID de Contacto": "contact_id",
        "Team": "team_id",
        "CSAT": "csat_score",
        "ID Cesionario": "cesionario_id",
        "CSAT Follow Up Feedback": "feedback",
        "Tiempo de resolución": "tiempo_resolucion",
        "Tipificacion": "tipificacion",
        "Resumen": "resumen",
    },
}


def parse_excel_file(file: UploadFile) -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    df = pd.read_excel(file.file, sheet_name=0)

    mapping_sheet = None
    try:
        mapping_sheet = pd.read_excel(file.file, sheet_name=1)
    except Exception:
        pass

    return df, mapping_sheet


def convert_external_ids(df: pd.DataFrame, spreadsheet_type: SpreadsheetType, db: Session):
    if spreadsheet_type == SpreadsheetType.CLOSED_CONVERSATIONS:
        df = _convert_closed_conversations(df, db)
    elif spreadsheet_type == SpreadsheetType.LIFECYCLES:
        df = _convert_lifecycles(df, db)
    elif spreadsheet_type == SpreadsheetType.ADS:
        df = _convert_ads(df, db)
    elif spreadsheet_type == SpreadsheetType.CSAT:
        df = _convert_csat(df, db)

    return df


def _convert_closed_conversations(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    df = df.copy()
    contact_ids = []
    canal_ids = []
    cesionario_ids = []
    equipo_ids = []

    for _, row in df.iterrows():
        contact_id_val = row.get("ID de Contacto")
        canal_val = row.get("Canal")
        cesionario_val = row.get("Cesionario")
        equipo_val = row.get("Equipo")

        contact_internal_id = None
        canal_internal_id = None
        cesionario_internal_id = None
        equipo_internal_id = None

        if not pd.isna(contact_id_val):
            try:
                contact_id = int(float(contact_id_val))
                telefono_val = row.get("Telefono")
                telefono_str = None
                if not pd.isna(telefono_val):
                    try:
                        telefono_str = str(int(float(telefono_val)))
                    except (ValueError, TypeError):
                        telefono_str = str(telefono_val)

                email_val = row.get("Correo electronico")
                email_str = str(email_val) if not pd.isna(email_val) else None

                contact_internal_id = get_or_create_contact(
                    db,
                    contact_id,
                    nombre=row.get("Nombre"),
                    email=email_str,
                    telefono=telefono_str,
                )
            except (ValueError, TypeError):
                pass

        if not pd.isna(canal_val):
            try:
                canal_ext_id = int(float(canal_val))
                canal_internal_id = get_or_create_channel(db, canal_ext_id)
            except (ValueError, TypeError):
                pass

        if not pd.isna(cesionario_val):
            cesionario_str = str(cesionario_val).strip()
            if cesionario_str and cesionario_str.lower() != "undefined":
                parts = cesionario_str.split(" ")
                if parts and parts[0].isdigit():
                    try:
                        agent_ext_id = int(parts[0])
                        cesionario_internal_id = get_or_create_agent(db, agent_ext_id, cesionario_str)
                    except ValueError:
                        pass
                else:
                    agent = db.query(Agent).filter(Agent.name.ilike(cesionario_str)).first()
                    if agent:
                        cesionario_internal_id = agent.id

        if not pd.isna(equipo_val):
            try:
                team_ext_id = int(float(equipo_val))
                equipo_internal_id = get_or_create_team(db, team_ext_id)
            except (ValueError, TypeError):
                pass

        contact_ids.append(contact_internal_id)
        canal_ids.append(canal_internal_id)
        cesionario_ids.append(cesionario_internal_id)
        equipo_ids.append(equipo_internal_id)

    df["contact_id"] = pd.Series(contact_ids, dtype="Int64")
    df["Canal"] = pd.Series(canal_ids, dtype="Int64")
    df["Cesionario"] = pd.Series(cesionario_ids, dtype="Int64")
    df["Equipo"] = pd.Series(equipo_ids, dtype="Int64")

    return df


def _convert_lifecycles(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    df = df.copy()
    contact_ids = []

    for _, row in df.iterrows():
        contact_id_val = row.get("ID de Contacto")
        contact_internal_id = None

        if not pd.isna(contact_id_val):
            try:
                contact_id = int(float(contact_id_val))
                telefono_val = row.get("Telefono")
                telefono_str = None
                if not pd.isna(telefono_val):
                    try:
                        telefono_str = str(int(float(telefono_val)))
                    except (ValueError, TypeError):
                        telefono_str = str(telefono_val)

                email_val = row.get("Correo electronico")
                email_str = str(email_val) if not pd.isna(email_val) else None

                contact_internal_id = get_or_create_contact(
                    db,
                    contact_id,
                    nombre=row.get("Nombre"),
                    email=email_str,
                    telefono=telefono_str,
                )
            except (ValueError, TypeError):
                pass

        contact_ids.append(contact_internal_id)

    df["contact_id"] = pd.Series(contact_ids, dtype="Int64")

    return df


def _convert_ads(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    df = df.copy()
    contact_ids = []
    agente_ids = []

    for _, row in df.iterrows():
        contact_id_val = row.get("Contact ID")
        agente_val = row.get("Agente")
        contact_internal_id = None
        agente_internal_id = None

        if not pd.isna(contact_id_val):
            try:
                contact_id = int(float(contact_id_val))
                nombre = row.get("Nombre") if not pd.isna(row.get("Nombre")) else None
                telefono_val = row.get("Telefono")
                telefono_str = None
                if not pd.isna(telefono_val):
                    try:
                        telefono_str = str(int(float(telefono_val)))
                    except (ValueError, TypeError):
                        telefono_str = str(telefono_val)
                contact_internal_id = get_or_create_contact(db, contact_id, nombre=nombre, telefono=telefono_str)
            except (ValueError, TypeError):
                pass

        if not pd.isna(agente_val):
            agente_str = str(agente_val).strip()
            if agente_str:
                agente = db.query(Agent).filter(Agent.name.ilike(agente_str)).first()
                if agente:
                    agente_internal_id = agente.id
                else:
                    agente_internal_id = get_or_create_agent(db, None, agente_str)

        contact_ids.append(contact_internal_id)
        agente_ids.append(agente_internal_id)

    df["contact_id"] = pd.Series(contact_ids, dtype="Int64")
    df["Agente"] = pd.Series(agente_ids, dtype="Int64")

    return df


def _convert_csat(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    df = df.copy()
    contact_ids = []
    cesionario_ids = []
    team_ids = []

    for _, row in df.iterrows():
        contact_id_val = row.get("ID de Contacto")
        cesionario_val = row.get("ID Cesionario")
        team_val = row.get("Team")
        contact_internal_id = None
        cesionario_internal_id = None
        team_internal_id = None

        if not pd.isna(contact_id_val):
            try:
                contact_id = int(float(contact_id_val))
                contact_internal_id = get_or_create_contact(db, contact_id)
            except (ValueError, TypeError):
                pass

        if not pd.isna(cesionario_val):
            try:
                agent_id = int(float(cesionario_val))
                cesionario_internal_id = get_or_create_agent(db, agent_id)
            except (ValueError, TypeError):
                pass

        if not pd.isna(team_val):
            try:
                team_id = int(float(team_val))
                team_internal_id = get_or_create_team(db, team_id)
            except (ValueError, TypeError):
                pass

        contact_ids.append(contact_internal_id)
        cesionario_ids.append(cesionario_internal_id)
        team_ids.append(team_internal_id)

    df["contact_id"] = pd.Series(contact_ids, dtype="Int64")
    df["ID Cesionario"] = pd.Series(cesionario_ids, dtype="Int64")
    df["Team"] = pd.Series(team_ids, dtype="Int64")

    return df


@router.post("/{spreadsheet_type}", response_model=ImportResponse)
async def import_spreadsheet(
    spreadsheet_type: SpreadsheetType,
    file: UploadFile,
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
    token_data: TokenPayload = Depends(verify_jwt),
):
    """
    Importa un archivo Excel y lo guarda en la base de datos.

    - **spreadsheet_type**: Tipo de spreadsheet (closed_conversations, lifecycles, ads, csat)
    - **file**: Archivo Excel (.xlsx, .xls)

    Retorna el número de registros importados y cualquier error encontrado.
    """

    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)

    max_file_size = 10 * 1024 * 1024
    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el límite de 10MB",
        )

    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos Excel (.xlsx, .xls)",
        )

    try:
        df, mapping_df = parse_excel_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al leer el archivo: {str(e)}",
        ) from e

    df = convert_external_ids(df, spreadsheet_type, db)
    db.commit()

    columns: dict[str, str] = COLUMN_MAPPING[spreadsheet_type]

    errors: list[str] = []
    rows_imported = 0

    def validate_row(row_data: dict, row_num: int) -> tuple[bool, str | None]:
        if not row_data.get("contact_id"):
            return False, f"Fila {row_num}: contact_id es requerido"
        if not isinstance(row_data.get("contact_id"), int):
            return False, f"Fila {row_num}: contact_id debe ser un número entero"
        return True, None

    try:
        batch_size = 100
        has_contact_col = "contact_id" in df.columns
        for _, row in df.iterrows():
            try:
                data: dict[str, object] = {}

                if has_contact_col:
                    contact_val = row.get("contact_id")
                    if contact_val is not None and not pd.isna(contact_val):
                        try:
                            data["contact_id"] = int(contact_val)
                        except (ValueError, TypeError):
                            data["contact_id"] = None
                    else:
                        data["contact_id"] = None

                for excel_col, db_col in columns.items():
                    if db_col not in data:
                        data[db_col] = None

                    if excel_col in row.index:
                        val = row[excel_col]
                        if pd.isna(val):
                            data[db_col] = None
                        else:
                            if db_col == "fecha":
                                if isinstance(val, datetime):
                                    data[db_col] = val
                                else:
                                    data[db_col] = pd.to_datetime(val)
                            elif db_col == "ad_timestamp":
                                if isinstance(val, int | float):
                                    timestamp_ms = int(val)
                                    try:
                                        data[db_col] = datetime.fromtimestamp(timestamp_ms / 1000)
                                    except (ValueError, OSError):
                                        data[db_col] = None
                                else:
                                    data[db_col] = None
                            elif db_col == "tiempo_resolucion":
                                if isinstance(val, str):
                                    try:
                                        parts = val.split(":")
                                        if len(parts) == 3:
                                            seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                                        elif len(parts) == 2:
                                            seconds = int(parts[0]) * 60 + int(parts[1])
                                        else:
                                            seconds = int(parts[0])
                                        data[db_col] = seconds
                                    except (ValueError, TypeError):
                                        data[db_col] = None
                                else:
                                    data[db_col] = None
                            elif db_col in ("canal_id", "cesionario_id", "equipo_id"):
                                if pd.isna(val):
                                    data[db_col] = None
                                else:
                                    try:
                                        data[db_col] = int(float(val))
                                    except (ValueError, TypeError):
                                        data[db_col] = None
                            elif db_col == "contact_id":
                                continue

                            elif db_col in (
                                "ad_channel_id",
                                "ad_channel_type",
                                "ad_contact_type",
                                "ad_adset_id",
                                "ad_adset_name",
                                "ad_ad_url",
                                "ad_status",
                            ):
                                data[db_col] = str(val) if not pd.isna(val) else None
                            else:
                                data[db_col] = val

                is_valid, error_msg = validate_row(data, rows_imported + 1)
                if not is_valid:
                    errors.append(error_msg)
                    continue

                if spreadsheet_type == SpreadsheetType.CLOSED_CONVERSATIONS:
                    record = ClosedConversation(**data)
                elif spreadsheet_type == SpreadsheetType.LIFECYCLES:
                    record = Lifecycle(**data)
                elif spreadsheet_type == SpreadsheetType.ADS:
                    record = Ad(**data)
                elif spreadsheet_type == SpreadsheetType.CSAT:
                    record = CSAT(**data)

                db.add(record)
                rows_imported += 1

                if rows_imported % batch_size == 0:
                    db.commit()

            except Exception as e:
                errors.append(f"Fila {rows_imported + 1}: {str(e)}")

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la transacción: {str(e)}",
        ) from e

    return ImportResponse(
        success=len(errors) == 0,
        message=f"Importación completada: {rows_imported} registros",
        rows_imported=rows_imported,
        rows_failed=len(errors),
        errors=errors[:10],
    )


@router.get("/templates/{spreadsheet_type}", response_model=ImportTemplateResponse)
def get_template(
    spreadsheet_type: SpreadsheetType,
    _: str = Depends(verify_api_key),
):
    """
    Obtiene la plantilla de importación para un tipo de spreadsheet.

    - **spreadsheet_type**: Tipo de spreadsheet (closed_conversations, lifecycles, ads, csat)

    Retorna las columnas esperadas y un ejemplo de datos.
    """
    templates = {
        SpreadsheetType.CLOSED_CONVERSATIONS: {
            "columns": [
                "Fecha",
                "ID de Contacto",
                "Nombre",
                "Correo electronico",
                "Telefono",
                "Canal",
                "Cesionario",
                "Equipo",
                "Tipificacion",
                "Resumen",
            ],
            "sample_data": [
                {
                    "Fecha": "2025-01-01 10:00:00",
                    "ID de Contacto": 123456,
                    "Nombre": "Juan Perez",
                    "Correo electronico": "juan@email.com",
                    "Telefono": "+1234567890",
                    "Canal": 440334,
                    "Cesionario": "905321 ai_agent",
                    "Equipo": 34369,
                    "Tipificacion": "Consulta general",
                    "Resumen": "Resumen de la conversación",
                }
            ],
        },
        SpreadsheetType.LIFECYCLES: {
            "columns": [
                "Fecha",
                "ID de Contacto",
                "Ciclo de vida",
                "Nombre",
                "Correo electronico",
                "Telefono",
                "PAis",
                "Cesionario",
                "Vendedor",
                "Canal",
            ],
            "sample_data": [
                {
                    "Fecha": "2025-01-01 10:00:00",
                    "ID de Contacto": 123456,
                    "Ciclo de vida": "Hot Lead",
                    "Nombre": "Juan Perez",
                    "Correo electronico": "juan@email.com",
                    "Telefono": "+1234567890",
                    "PAis": "Venezuela",
                    "Cesionario": "Alessandra Barrios",
                    "Vendedor": "",
                    "Canal": "",
                }
            ],
        },
        SpreadsheetType.ADS: {
            "columns": [
                "Contact ID",
                "Telefono",
                "Nombre",
                "Agente",
                "{{$clicktochat.ad_timestamp}} ",
                "{{$clicktochat.ad_channel_id}}",
                "{{$clicktochat.ad_channel_type}}",
                "{{$clicktochat.ad_contact_type}}",
                "{{$clicktochat.ad_adset_id}}",
                "{{$clicktochat.ad_adset_name}}",
                "{{$clicktochat.ad_ad_url}}",
                "{{$clicktochat.ad_status}}",
            ],
            "sample_data": [
                {
                    "Contact ID": 123456,
                    "Telefono": "+1234567890",
                    "Nombre": "Juan Perez",
                    "Agente": "Emilis Sanchez",
                    "{{$clicktochat.ad_timestamp}} ": 1764228695956003,
                    "{{$clicktochat.ad_channel_id}}": 440224,
                    "{{$clicktochat.ad_channel_type}}": "facebook",
                    "{{$clicktochat.ad_contact_type}}": "New Contact",
                    "{{$clicktochat.ad_adset_id}}": "120238666039440111",
                    "{{$clicktochat.ad_adset_name}}": "BlackFriday",
                    "{{$clicktochat.ad_ad_url}}": "https://example.com/ad",
                    "{{$clicktochat.ad_status}}": "ACTIVE",
                }
            ],
        },
        SpreadsheetType.CSAT: {
            "columns": [
                "ID de Contacto",
                "Fecha",
                "Team",
                "CSAT",
                "ID Cesionario",
                "CSAT Follow Up Feedback",
                "Tiempo de resolución",
                "Tipificacion",
                "Resumen",
            ],
            "sample_data": [
                {
                    "ID de Contacto": 123456,
                    "Fecha": "2025-01-01 10:00:00",
                    "Team": 34369,
                    "CSAT": 5,
                    "ID Cesionario": 905321,
                    "CSAT Follow Up Feedback": "Excelente atención",
                    "Tiempo de resolución": "00:05:30",
                    "Tipificacion": "Consulta general",
                    "Resumen": "Caso resuelto satisfactoriamente",
                }
            ],
        },
    }

    template = templates.get(spreadsheet_type)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de spreadsheet no encontrado",
        )

    return ImportTemplateResponse(
        spreadsheet_type=spreadsheet_type,
        columns=template["columns"],
        sample_data=template["sample_data"],
    )
