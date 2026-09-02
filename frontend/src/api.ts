import type { ReconcileRequest, ReconcileResponse, ApiError } from './types';

const API_BASE_URL = '';

export interface ReconciliationError extends Error {
  statusCode: number;
}

function createReconciliationError(statusCode: number, message: string): ReconciliationError {
  const error = new Error(message) as ReconciliationError;
  error.name = 'ReconciliationError';
  error.statusCode = statusCode;
  return error;
}

function isReconciliationError(error: unknown): error is ReconciliationError {
  return error instanceof Error && error.name === 'ReconciliationError';
}

export async function reconcileExpenses(
  request: ReconcileRequest
): Promise<ReconcileResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/reconcile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw createReconciliationError(
        response.status,
        error.detail || 'Reconciliation failed'
      );
    }

    return await response.json();
  } catch (error) {
    if (isReconciliationError(error)) {
      throw error;
    }
    throw createReconciliationError(
      0,
      error instanceof Error ? error.message : 'Network error'
    );
  }
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return await response.json();
}

export interface AffidavitRequest {
  vendor: string;
  price: number;
  date: string;  // YYYY-MM-DD
  cardholder_name: string;
}

export async function generateAffidavit(request: AffidavitRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/generate-affidavit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMessage = 'Failed to generate affidavit';
    try {
      const error = await response.json();
      errorMessage = error.detail || errorMessage;
    } catch {
      errorMessage = `${errorMessage}: ${response.statusText}`;
    }
    throw new Error(errorMessage);
  }

  return await response.blob();
}
