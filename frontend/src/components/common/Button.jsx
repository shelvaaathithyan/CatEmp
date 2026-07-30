import styles from './Button.module.css';

const Button = ({ children, type = 'button', variant = 'primary', isLoading = false, className = '', ...props }) => {
  return (
    <button
      type={type}
      className={`${styles.button} ${styles[variant]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
};

export default Button;
