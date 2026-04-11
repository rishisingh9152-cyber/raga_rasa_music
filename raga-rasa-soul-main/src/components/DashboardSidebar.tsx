import { NavLink, useNavigate } from "react-router-dom";
import { Home, User, Music, PlayCircle, Upload, X } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const links = [
  { to: "/dashboard/home", icon: Home, label: "Home" },
  { to: "/dashboard/profile", icon: User, label: "Profile" },
  { to: "/dashboard/player", icon: Music, label: "Music Player" },
  { to: "/dashboard/upload", icon: Upload, label: "Upload Song" },
  { to: "/dashboard/session", icon: PlayCircle, label: "Start Session" },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

const DashboardSidebar = ({ open, onClose }: Props) => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 bg-background/60 backdrop-blur-sm z-40 lg:hidden" onClick={onClose} />
      )}

      <aside
        className={`fixed top-0 left-0 h-full w-64 glass-card rounded-none border-l-0 border-t-0 border-b-0 z-50 flex flex-col transition-transform duration-300 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        } lg:sticky lg:top-0 lg:h-screen`}
      >
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2
            onClick={() => navigate("/")}
            className="font-display text-xl font-bold gradient-text cursor-pointer transition-all duration-200 hover:drop-shadow-[0_0_8px_hsl(265,80%,65%,0.5)]"
          >
            Raga-Rasa-Laya
          </h2>
          <button onClick={onClose} className="lg:hidden text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={onClose}
              className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            >
              <link.icon className="w-5 h-5" />
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full gradient-bg flex items-center justify-center text-primary-foreground font-bold text-sm">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">{user?.email || 'User'}</p>
              <p className="text-xs text-muted-foreground">Free Plan</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default DashboardSidebar;
