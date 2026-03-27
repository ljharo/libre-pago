from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import TokenPayload, verify_api_key, verify_jwt
from app.models import CSAT, Ad, Agent, Channel, ClosedConversation, Lifecycle, Team
from app.schemas.import_ import ImportResponse, ImportTemplateResponse, SpreadsheetType

router = APIRouter(prefix="/api/import", tags=["import"])

COLUMN_MAPPING = {
    SpreadsheetType.CLOSED_CONVERSATIONS: {
        "Fecha": "fecha",
        "ID de Contacto": "contact_id",
        "Nombre": "nombre",
        "Correo electronico": "email",
        "Telefono": "telefono",
        "Canal": "canal_id",
        "Cesionario": "cesionario_id",
        "Equipo": "equipo_id",
        "Tipificacion": "tipificacion",
        "Resumen": "resumen",
    },
    SpreadsheetType.LIFECYCLES: {
        "Fecha": "fecha",
        "ID de Contacto": "contact_id",
        "Ciclo de vida": "ciclo_vida",
        "Nombre": "nombre",
        "Correo electronico": "email",
        "Telefono": "telefono",
        "PAis": "pais",
        "Cesionario": "cesionario",
        "Vendedor": "vendedor",
        "Canal": "canal",
    },
    SpreadsheetType.ADS: {
        "Contact ID": "contact_id",
        "Telefono": "telefono",
        "Nombre": "nombre",
        "Agente": "agente_id",
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
        "ID de Contacto": "contact_id",
        "Fecha": "fecha",
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
    canal_map = {int(row.channel_id): row.id for row in db.query(Channel).all()}
    agent_map = {int(row.agent_id): row.id for row in db.query(Agent).all()}
    team_map = {int(row.team_id): row.id for row in db.query(Team).all()}

    def parse_agent(val):
        if pd.isna(val):
            return None
        val_str = str(val).strip()
        if not val_str or val_str.lower() == "undefined":
            return None
        parts = val_str.split(" ")
        if parts and parts[0].isdigit():
            ext_id = int(parts[0])
            return agent_map.get(ext_id)
        try:
            return agent_map.get(int(float(val)))
        except (ValueError, TypeError):
            return None

    def parse_canal(val):
        if pd.isna(val):
            return None
        try:
            int_val = int(float(val))
            return canal_map.get(int_val)
        except (ValueError, TypeError):
            return None

    def parse_team(val):
        if pd.isna(val):
            return None
        try:
            int_val = int(float(val))
            return team_map.get(int_val)
        except (ValueError, TypeError):
            return None

    df["Canal"] = df["Canal"].apply(parse_canal)
    df["Cesionario"] = df["Cesionario"].apply(parse_agent)
    df["Equipo"] = df["Equipo"].apply(parse_team)

    return df


def _convert_lifecycles(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    agent_name_map = {row.name.lower(): row.id for row in db.query(Agent).all()}

    def parse_cesionario(val):
        if pd.isna(val):
            return None
        val_str = str(val).strip()
        if val_str.lower() in ("undefined undefined", "nan", ""):
            return None
        agent_id = agent_name_map.get(val_str.lower())
        return agent_id

    df["Cesionario"] = df["Cesionario"].apply(parse_cesionario)

    return df


def _convert_ads(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    agent_name_map = {row.name.lower(): row.id for row in db.query(Agent).all()}

    def parse_agent(val):
        if pd.isna(val):
            return None
        val_str = str(val).strip()
        return agent_name_map.get(val_str.lower())

    def parse_timestamp(val):
        if pd.isna(val):
            return None
        try:
            unix_val = float(val)
            return datetime.fromtimestamp(unix_val / 1000)
        except (ValueError, OSError):
            return None

    df["Agente"] = df["Agente"].apply(parse_agent)
    df["{{$clicktochat.ad_timestamp}} "] = df["{{$clicktochat.ad_timestamp}} "].apply(parse_timestamp)

    return df


def _convert_csat(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    agent_map = {int(row.agent_id): row.id for row in db.query(Agent).all()}
    team_map = {int(row.team_id): row.id for row in db.query(Team).all()}

    def parse_agent(val):
        if pd.isna(val):
            return None
        try:
            return agent_map.get(int(float(val)))
        except (ValueError, TypeError):
            return None

    def parse_team(val):
        if pd.isna(val):
            return None
        try:
            return team_map.get(int(float(val)))
        except (ValueError, TypeError):
            return None

    def parse_time(val):
        if pd.isna(val):
            return None
        val_str = str(val)
        try:
            parts = val_str.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except (ValueError, IndexError):
            pass
        return None

    df["ID Cesionario"] = df["ID Cesionario"].apply(parse_agent)
    df["Team"] = df["Team"].apply(parse_team)
    df["Tiempo de resolución"] = df["Tiempo de resolución"].apply(parse_time)

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

    columns: dict[str, str] = COLUMN_MAPPING[spreadsheet_type]

    errors: list[str] = []
    rows_imported = 0

    def validate_row(row_data: dict, row_num: int) -> tuple[bool, str | None]:
        if not row_data.get("contact_id"):
            return False, f"Fila {row_num}: contact_id es requerido"
        if not isinstance(row_data.get("contact_id"), int | float):
            try:
                int(row_data["contact_id"])
            except (ValueError, TypeError):
                return False, f"Fila {row_num}: contact_id debe ser un número"
        if row_data.get("nombre") and not isinstance(row_data.get("nombre"), str):
            return False, f"Fila {row_num}: nombre debe ser texto"
        return True, None

    try:
        batch_size = 100
        for _, row in df.iterrows():
            try:
                data: dict[str, object] = {}
                for excel_col, db_col in columns.items():
                    if db_col not in data:
                        data[db_col] = None

                    if excel_col in row.index:
                        val = row[excel_col]
                        if pd.isna(val):  # type: ignore[call-overload]
                            data[db_col] = None
                        else:
                            if db_col == "fecha":
                                if isinstance(val, datetime):
                                    data[db_col] = val
                                else:
                                    data[db_col] = pd.to_datetime(val)
                            elif db_col in ("canal_id", "cesionario_id", "equipo_id"):
                                if pd.isna(val):
                                    data[db_col] = None
                                else:
                                    try:
                                        data[db_col] = int(float(val))
                                    except (ValueError, TypeError):
                                        data[db_col] = None
                            elif db_col == "contact_id":
                                try:
                                    data[db_col] = int(float(val))
                                except (ValueError, TypeError):
                                    data[db_col] = None
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
