import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import gsap from 'gsap';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import { useAuth } from '../../context/AuthContext';
import styles from './Login.module.css';
import CatLogo from '../../assets/logos/catlogo.png';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const leftPanelRef = useRef(null);
  const rightPanelRef = useRef(null);

  useEffect(() => {
    gsap.fromTo(leftPanelRef.current, 
      { opacity: 0, y: 15 }, 
      { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out' }
    );
    
    gsap.fromTo(rightPanelRef.current, 
      { opacity: 0, y: 15 }, 
      { opacity: 1, y: 0, duration: 0.45, ease: 'power2.out', delay: 0.1 }
    );
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter both email and password.');
      return;
    }

    setIsLoading(true);
    try {
      const user = await login(email, password);
      toast.success('Successfully logged in.');
      
      if (user.role === 'Dealer' || user.role === 'CatAdmin') navigate('/dealer/dashboard');
      else if (user.role === 'Customer') navigate('/customer/dashboard');
      else if (user.role === 'Fleet Manager') navigate('/fleet/dashboard');
      else {
        toast.warning('Unknown role. Please contact support.');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <div className={styles.leftPanel}>
        <div className={styles.hero} ref={leftPanelRef}>
          <div className={styles.logoWrapper}>
            <img src={CatLogo} alt="Caterpillar" className={styles.catLogo} />
          </div>
          <h1 className={styles.title}>
            Manage Equipment <br/>
            <span className={styles.titleHighlight}>with Confidence.</span>
          </h1>
          <p className={styles.description}>
            Track rentals, monitor machine health, and optimize your entire fleet operations from one unified platform.
          </p>
        </div>
      </div>
      
      <div className={styles.rightPanel}>
        <div className={styles.loginCard} ref={rightPanelRef}>
          <h2 className={styles.loginTitle}>Welcome.</h2>
          <p className={styles.loginSubtitle}>
            Sign in to your enterprise account.
          </p>
          
          <form onSubmit={handleLogin} className={styles.form}>
            <div className={styles.emailWrapper}>
              <Input
                label="Email Address"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div className={styles.passwordWrapper}>
              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            
            <div className={styles.submitWrapper}>
              <Button type="submit" isLoading={isLoading} className={styles.submitBtn}>
                Sign In
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
