import styles from './Card.module.css';

const Card = ({ title, children, className = '' }) => {
  return (
    <div className={`${styles.card} ${className}`}>
      {title && (
        <div className={styles.cardHeader}>
          <h3 className={styles.cardTitle}>{title}</h3>
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
