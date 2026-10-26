import { useState } from 'react';
import type { FormEvent } from 'react';
import { reconcileExpenses } from '../api';
import type { ReconcileResponse } from '../types';
import AffidavitsModal from './AffidavitsModal';
import { parseExpectedExpenses, type ParsedExpense } from '../utils/parseExpenses';

interface ExpenseFormProps {
  onSuccess: (response: ReconcileResponse, cardholderName: string) => void;
  onError: (error: string) => void;
  onLoadingChange: (loading: boolean) => void;
}

export default function ExpenseForm({
  onSuccess,
  onError,
  onLoadingChange,
}: ExpenseFormProps) {
  const [cardholderName, setCardholderName] = useState('');
  const [startDate, setStartDate] = useState('');
  const [sheetLink, setSheetLink] = useState('');
  const [expectedExpenses, setExpectedExpenses] = useState('');
  const [showAffidavitsModal, setShowAffidavitsModal] = useState(false);
  const [parsedExpenses, setParsedExpenses] = useState<ParsedExpense[]>([]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    onLoadingChange(true);

    try {
      const response = await reconcileExpenses({
        cardholder_name: cardholderName,
        start_date: startDate,
        expected_expenses: expectedExpenses,
        sheet_link: sheetLink,
      });
      onSuccess(response, cardholderName);
    } catch (error) {
      if (error instanceof Error) {
        onError(error.message);
      } else {
        onError('An unexpected error occurred');
      }
    } finally {
      onLoadingChange(false);
    }
  };

  const handleGenerateAffidavits = () => {
    // Validate form fields
    if (!cardholderName || !startDate || !sheetLink || !expectedExpenses) {
      onError('Please fill out all fields before generating affidavits');
      return;
    }

    // Parse expected expenses
    const expenses = parseExpectedExpenses(expectedExpenses);

    if (expenses.length === 0) {
      onError('No valid expected expenses found. Check your formatting.');
      return;
    }

    setParsedExpenses(expenses);
    setShowAffidavitsModal(true);
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="expense-form">
      <div className="form-columns">
        <div className="form-column-left">
          <div className="form-group">
            <label htmlFor="cardholderName">Cardholder Name</label>
            <select
              id="cardholderName"
              value={cardholderName}
              onChange={(e) => setCardholderName(e.target.value)}
              required
            >
              <option value="">Select Cardholder</option>
              <option value="Gavin Firestone (Treasurer)">Gavin Firestone (Treasurer)</option>
              <option value="Gopi Amin (Treasurer)">Gopi Amin (Treasurer)</option>
              <option value="Sami Johnson (President)">Sami Johnson (President)</option>
              <option value="Allie Meachum (IVP)">Allie Meachum (IVP)</option>
              <option value="Jesse Romero (EVP)">Jesse Romero (EVP)</option>
              <option value="Vero Paz Agreda (CVP)">Vero Paz Agreda (CVP)</option>
              <option value="Atticus Rothschild (Socials)">Atticus Rothschild (Socials)</option>
              <option value="Ashley Yang (Socials)">Ashley Yang (Socials)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              id="startDate"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="sheetLink">Purchase Form Spreadsheet Link</label>
            <input
              id="sheetLink"
              type="url"
              value={sheetLink}
              onChange={(e) => setSheetLink(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-column-right">
          <div className="form-group">
            <label htmlFor="expectedExpenses">Expenses (paste from Kristen's email, format if needed)</label>
            <textarea
              id="expectedExpenses"
              value={expectedExpenses}
              onChange={(e) => setExpectedExpenses(e.target.value)}
              rows={10}
              placeholder="Ex. 11/1/25 - Target - $25.00"
              required
            />
            <small>Format: MM/DD/YY - Vendor - $Price (one per line - note only 2 digits for year)</small>
          </div>
        </div>
      </div>

      <div className="form-button-container">
        <button
          type="button"
          onClick={handleGenerateAffidavits}
          className="submit-button secondary-button"
        >
          Generate Affidavits
        </button>
        <button type="submit" className="submit-button">
          Reconcile Expenses
        </button>
      </div>
      </form>

      {showAffidavitsModal && (
        <AffidavitsModal
          expenses={parsedExpenses}
          cardholderName={cardholderName}
          onClose={() => setShowAffidavitsModal(false)}
        />
      )}
    </>
  );
}
