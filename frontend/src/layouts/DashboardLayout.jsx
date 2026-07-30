import { useRef, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bell } from 'lucide-react';
import gsap from 'gsap';
import styles from './Layout.module.css';
import CatLogo from '../assets/logos/catlogo.png';

const DashboardLayout = ({ title, links }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const contentRef = useRef(null);

  useEffect(() => {
    // GSAP Page Fade-in on route change
    gsap.fromTo(contentRef.current, 
      { opacity: 0, y: 10 }, 
      { opacity: 1, y: 0, duration: 0.35, ease: 'power2.out' }
    );
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={styles.layout}>
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <img src={CatLogo} alt="Caterpillar" className={styles.logo} />
        </div>
        <nav className={styles.navLinks}>
          {links.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              end={link.path.endsWith('dashboard')}
              className={({ isActive }) => 
                isActive ? `${styles.navLink} ${styles.navLinkActive}` : styles.navLink
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      
      <div className={styles.mainWrapper}>
        <header className={styles.navbar}>
          <div className={styles.navActions}>
            <button 
              className={styles.notificationBtn} 
              onClick={() => navigate('notifications')}
              title="Notifications"
            >
              <Bell size={20} />
              <span className={styles.notificationDot}></span>
            </button>
            
            {user && (
              <div className={styles.userInfo}>
                <span className={styles.userName}>{user.name}</span>
                <span className={styles.userRole}>{user.role === 'staff' ? 'Admin' : user.role === 'fleet manager' ? 'Fleet Manager' : user.role}</span>
              </div>
            )}
            <button onClick={handleLogout} className={styles.logoutBtn}>Logout</button>
          </div>
        </header>
        <main className={styles.contentWrapper} ref={contentRef}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
