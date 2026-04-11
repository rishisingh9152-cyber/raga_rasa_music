import { Menu, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useSession } from "@/context/SessionContext";
import { useAuth } from "@/context/AuthContext";

interface Props {
  onMenuClick: () => void;
}

const DashboardTopbar = ({ onMenuClick }: Props) => {
  const navigate = useNavigate();
  const { session } = useSession();
  const { logout } = useAuth();

  return (
    <header className="h-14 border-b border-border flex items-center justify-between px-4 md:px-6 bg-card/50 backdrop-blur-md sticky top-0 z-30">
      <button onClick={onMenuClick} className="lg:hidden text-muted-foreground">
        <Menu className="w-5 h-5" />
      </button>

      <div className="hidden lg:block" />

      <div className="flex items-center gap-4">
        <button
          onClick={() => {
            logout();
            navigate('/');
          }}
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          title="Logout"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default DashboardTopbar;
