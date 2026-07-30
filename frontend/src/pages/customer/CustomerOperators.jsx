import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { operatorAPI } from '../../api';

const CustomerOperators = () => {
  const [operators, setOperators] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOperators = async () => {
      try {
        const data = await operatorAPI.getAll();
        setOperators(data);
      } catch (error) {
        console.error("Error fetching operators:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchOperators();
  }, []);

  const columns = [
    { header: 'Operator ID', accessor: 'operator_id' },
    { 
      header: 'Operator Name', 
      accessor: 'operator_name',
      cell: (row) => <span style={{ fontWeight: 'bold' }}>{row.operator_name}</span>
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>My Operators</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Manage drivers and operators for your rented machines.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading operators...</div>
        ) : (
          <Table columns={columns} data={operators} />
        )}
      </Card>
    </div>
  );
};

export default CustomerOperators;
