import React from 'react';
import styles from './Input.module.css';

const Input = React.forwardRef(({ label, error, className = '', ...props }, ref) => {
  return (
    <div className={`${styles.container} ${className}`}>
      {label && <label className={styles.label}>{label}</label>}
      <input
        ref={ref}
        className={`${styles.input} ${error ? styles.inputError : ''}`}
        {...props}
      />
      {error && <span className={styles.error}>{error}</span>}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
