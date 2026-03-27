import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { importApi } from '../lib/api';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, Loader2 } from 'lucide-react';

type SpreadsheetType = 'closed_conversations' | 'lifecycles' | 'ads' | 'csat';

const SPREADSHEET_TYPES: { value: SpreadsheetType; label: string }[] = [
  { value: 'closed_conversations', label: 'Conversaciones Cerradas' },
  { value: 'lifecycles', label: 'Ciclos de Vida (Lifecycles)' },
  { value: 'ads', label: 'Publicidad (Ads)' },
  { value: 'csat', label: 'Satisfacción (CSAT)' },
];

interface ImportResult {
  success: boolean;
  message: string;
  details?: {
    total_rows: number;
    inserted: number;
    updated: number;
    errors: string[];
  };
}

export default function ImportPage() {
  const [selectedType, setSelectedType] = useState<SpreadsheetType>('closed_conversations');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
        setError('Solo se permiten archivos Excel (.xlsx, .xls)');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('El archivo no puede superar 10MB');
        return;
      }
      setFile(selectedFile);
      setError('');
      setResult(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError('Selecciona un archivo');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await importApi.import(selectedType, file);
      setResult(response.data);
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || 'Error al importar el archivo');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await importApi.templates(selectedType);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${selectedType}_template.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Error al descargar la plantilla');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-white hover:underline"
            >
              ← Volver
            </button>
            <h1 className="text-2xl font-bold">Importar Datos</h1>
          </div>
        </div>
      </nav>

      <div className="container mx-auto p-6 max-w-2xl">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-6">Cargar Archivo Excel</h2>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de datos
            </label>
            <select
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value as SpreadsheetType);
                setFile(null);
                setResult(null);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {SPREADSHEET_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Archivo Excel
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto text-gray-400 mb-2" size={32} />
                {file ? (
                  <div className="flex items-center justify-center gap-2 text-green-600">
                    <FileSpreadsheet size={20} />
                    <span>{file.name}</span>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600">Haz clic para seleccionar un archivo</p>
                    <p className="text-sm text-gray-400">Máximo 10MB</p>
                  </div>
                )}
              </label>
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {result && (
            <div className={`mb-4 p-4 rounded ${result.success ? 'bg-green-100' : 'bg-red-100'}`}>
              <div className="flex items-center gap-2">
                {result.success ? (
                  <CheckCircle className="text-green-600" size={20} />
                ) : (
                  <XCircle className="text-red-600" size={20} />
                )}
                <span className={`font-semibold ${result.success ? 'text-green-700' : 'text-red-700'}`}>
                  {result.message}
                </span>
              </div>
              {result.details && (
                <div className="mt-2 text-sm text-gray-700">
                  <p>Total de filas: {result.details.total_rows}</p>
                  <p>Insertadas: {result.details.inserted}</p>
                  <p>Actualizadas: {result.details.updated}</p>
                  {result.details.errors.length > 0 && (
                    <div className="mt-2">
                      <p className="font-medium">Errores:</p>
                      <ul className="list-disc list-inside">
                        {result.details.errors.slice(0, 5).map((err, idx) => (
                          <li key={idx}>{err}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={handleDownloadTemplate}
              className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
            >
              Descargar Plantilla
            </button>
            <button
              onClick={handleImport}
              disabled={!file || loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Importando...
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Importar
                </>
              )}
            </button>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Información</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• El archivo debe ser un Excel (.xlsx o .xls)</li>
            <li>• La primera fila debe contener los nombres de columnas</li>
            <li>• La segunda hoja (opcional) puede contener mapeos de IDs externos</li>
            <li>• Máximo 10MB por archivo</li>
            <li>• Para Ads, las columnas especiales (clicktochat) se importan automáticamente</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
