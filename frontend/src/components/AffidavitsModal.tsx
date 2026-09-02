import { useState } from 'react';
import type { ParsedExpense } from '../utils/parseExpenses';
import { generateAffidavit } from '../api';
import '../styles/Modal.css';

interface AffidavitsModalProps {
  expenses: ParsedExpense[];
  cardholderName: string;
  onClose: () => void;
}

export default function AffidavitsModal({ expenses, cardholderName, onClose }: AffidavitsModalProps) {
  const [downloading, setDownloading] = useState<Set<number>>(new Set());

  const handleDownload = async (expense: ParsedExpense, index: number) => {
    setDownloading(prev => new Set(prev).add(index));

    try {
      const blob = await generateAffidavit({
        vendor: expense.vendor,
        price: expense.price,
        date: expense.date,
        cardholder_name: cardholderName,
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `affidavit_${expense.vendor.replace(/\s+/g, '_')}_${expense.date}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to generate affidavit:', error);
      alert(`Failed to generate affidavit for ${expense.vendor}`);
    } finally {
      setDownloading(prev => {
        const next = new Set(prev);
        next.delete(index);
        return next;
      });
    }
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h2>Generate Affidavits</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <table className="affidavits-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Vendor</th>
                <th>Price</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense, index) => (
                <tr key={index}>
                  <td>{new Date(expense.date).toLocaleDateString()}</td>
                  <td>{expense.vendor}</td>
                  <td>${expense.price.toFixed(2)}</td>
                  <td>
                    <button
                      className="download-button"
                      onClick={() => handleDownload(expense, index)}
                      disabled={downloading.has(index)}
                    >
                      {downloading.has(index) ? 'Downloading...' : 'Download'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
