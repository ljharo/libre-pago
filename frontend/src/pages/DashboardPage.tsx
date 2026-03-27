import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { conversationsApi, lifecyclesApi, adsApi, csatApi } from '../lib/api';
import {
  MessageSquare,
  TrendingUp,
  Target,
  ThumbsUp,
  Upload,
  Users,
  LogOut,
} from 'lucide-react';

interface Stats {
  conversations: { total: number; ai: number; human: number };
  lifecycles: { total: number };
  ads: { total: number; topCampaigns: { campaign: string; clicks: number }[] };
  csat: { average: number };
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    loadStats();
  }, [navigate]);

  const loadStats = async () => {
    try {
      const [conversations, lifecycles, ads, csat] = await Promise.all([
        conversationsApi.stats.monthly(),
        lifecyclesApi.stats.pipeline(),
        adsApi.stats.topCampaigns(),
        csatApi.stats.average(),
      ]);

      setStats({
        conversations: conversations.data,
        lifecycles: lifecycles.data,
        ads: ads.data,
        csat: csat.data,
      });
    } catch (err) {
      setError('Error al cargar las estadísticas');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-gray-600">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">LibrePago</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm">{user.username} ({user.role})</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-blue-700 px-3 py-1 rounded hover:bg-blue-800"
            >
              <LogOut size={18} />
              Salir
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto p-6">
        <h2 className="text-xl font-semibold mb-6">Dashboard</h2>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <MessageSquare className="text-blue-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Conversaciones</p>
                <p className="text-2xl font-bold">
                  {stats?.conversations?.total || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-4">
              <div className="bg-green-100 p-3 rounded-full">
                <TrendingUp className="text-green-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Ciclos de Vida</p>
                <p className="text-2xl font-bold">
                  {stats?.lifecycles?.total || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-4">
              <div className="bg-purple-100 p-3 rounded-full">
                <Target className="text-purple-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">Anuncios</p>
                <p className="text-2xl font-bold">{stats?.ads?.total || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center gap-4">
              <div className="bg-yellow-100 p-3 rounded-full">
                <ThumbsUp className="text-yellow-600" size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">CSAT Promedio</p>
                <p className="text-2xl font-bold">
                  {stats?.csat?.average?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Acciones Rápidas</h3>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => navigate('/import')}
                className="flex items-center gap-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50"
              >
                <Upload className="text-gray-600" size={24} />
                <span className="text-gray-700">Importar Datos</span>
              </button>
              <button
                onClick={() => navigate('/users')}
                className="flex items-center gap-2 p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50"
              >
                <Users className="text-gray-600" size={24} />
                <span className="text-gray-700">Gestionar Usuarios</span>
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Campañas Top</h3>
            <div className="space-y-3">
              {stats?.ads?.topCampaigns?.slice(0, 5).map((campaign, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <span className="text-gray-700 truncate">{campaign.campaign}</span>
                  <span className="font-semibold text-blue-600">{campaign.clicks} clics</span>
                </div>
              ))}
              {(!stats?.ads?.topCampaigns || stats.ads.topCampaigns.length === 0) && (
                <p className="text-gray-500">No hay datos disponibles</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
