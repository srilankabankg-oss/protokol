import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

function NavBar() {
  const navigate = useNavigate();
  const token = useAuthStore(s => s.token);
  const isAdmin = token ? (() => { try { const p = JSON.parse(atob(token.split('.')[1])); return p.role === 'admin'; } catch { return false; }})() : false;
  const logout = useAuthStore(s => s.logout);

  if (!token) return null;

  return (
    <nav className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-12">
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm font-bold text-blue-700 hover:text-blue-900">Книга добрых дел</Link>
          <Link to="/" className="text-xs text-gray-500 hover:text-gray-700">Совещания</Link>
          {isAdmin && <Link to="/admin" className="text-xs text-gray-500 hover:text-gray-700">Админка</Link>}
        </div>
        <button onClick={() => { logout(); navigate('/login'); }} className="text-xs text-gray-400 hover:text-red-500">Выйти</button>
      </div>
    </nav>
  );
}

export default NavBar;