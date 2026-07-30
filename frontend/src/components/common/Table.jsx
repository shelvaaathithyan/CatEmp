import styles from './Table.module.css';

const Table = ({ columns, data }) => {
  return (
    <div className={styles.tableContainer}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className={styles.th}>{col.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIdx) => (
            <tr key={rowIdx} className={styles.tr}>
              {columns.map((col, colIdx) => (
                <td key={colIdx} className={styles.td}>
                  {col.cell ? col.cell(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
