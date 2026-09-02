import { useState } from 'react';
import type { ReconcileResponse, ReportItem, ExpectedExpense } from '../types';
import { DndContext, PointerSensor, useSensor, useSensors, useDroppable, useDraggable, pointerWithin } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { generateAffidavit } from '../api';

interface ResultsViewProps {
  results: ReconcileResponse;
  cardholderName: string;
}

// Helper component for droppable zones
function DroppableZone({ id, children }: { id: string; children: React.ReactNode }) {
  const { isOver, setNodeRef } = useDroppable({
    id: id,
  });

  return (
    <div
      ref={setNodeRef}
      className={`droppable-zone ${isOver ? 'drag-over' : ''}`}
    >
      {children}
    </div>
  );
}

// Helper component for draggable actual expense cards
function DraggableActualCard({
  id,
  actual,
}: {
  id: string;
  actual: ReportItem;
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: id,
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="actual draggable-card"
    >
      <h4>Actual</h4>
      <p className="inline-info">
        <strong>Date:</strong> {actual.date} | <strong>Vendor:</strong> {actual.vendor} | <strong>Price:</strong> ${actual.price.toFixed(2)}
      </p>
      <p><strong>Description:</strong> {actual.description}</p>
      <p><strong>Activity:</strong> {actual.activity}</p>
      {(actual.receipts.length > 0 || actual.needsAffidavit) && (
        <p>
          <strong>Receipts:</strong>{' '}
          {actual.receipts.map((receipt, i) => (
            <span key={i}>
              {i > 0 && ', '}
              <a href={receipt} target="_blank" rel="noopener noreferrer">
                Receipt {i + 1}
              </a>
            </span>
          ))}
          {actual.needsAffidavit && (
            <span>
              {actual.receipts.length > 0 && ', '}
              Needs Affidavit
            </span>
          )}
        </p>
      )}
      {actual.flyer && (
        <p>
          <strong>Flyer:</strong>{' '}
          <a href={actual.flyer} target="_blank" rel="noopener noreferrer">
            View Flyer
          </a>
        </p>
      )}
    </div>
  );
}

export default function ResultsView({ results, cardholderName }: ResultsViewProps) {
  const [manualPairings, setManualPairings] = useState<Map<string, ReportItem>>(new Map());

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 1, // Minimal movement required to start drag (more responsive)
      },
    })
  );

  const handleDownloadAffidavit = async (expected: ExpectedExpense) => {
    try {
      const blob = await generateAffidavit({
        vendor: expected.vendor,
        price: expected.price,
        date: expected.date,
        cardholder_name: cardholderName,
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `affidavit_${expected.vendor.replace(/\s+/g, '_')}_${expected.date}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to generate affidavit:', error);
      alert('Failed to generate affidavit. Please try again.');
    }
  };

  const getExpectedId = (exp: ExpectedExpense, index: number) =>
    `${exp.date}-${exp.vendor}-${exp.price}-${index}`;

  // Create unique ID for actual expense
  const getActualId = (actual: ReportItem, index: number) =>
    `${actual.date}-${actual.vendor}-${actual.price}-${index}`;

  const getActualIndexFromId = (id: string): number => {
    const parts = id.split('-');
    return parseInt(parts[parts.length - 1]);
  };

  const isActualPaired = (actual: ReportItem, index: number): boolean => {
    const actualId = getActualId(actual, index);
    return Array.from(manualPairings.values()).some(
      (pairedItem) => getActualId(pairedItem, results.unmatched_actual.indexOf(pairedItem)) === actualId
    );
  };

  const availableActuals = results.unmatched_actual
    .map((actual, index) => ({ actual, originalIndex: index }))
    .filter(({ actual, originalIndex }) => !isActualPaired(actual, originalIndex));

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const actualIndex = getActualIndexFromId(active.id.toString());
    const expectedId = over.id.toString();
    const actualItem = results.unmatched_actual[actualIndex];

    setManualPairings(prev => {
      const newPairings = new Map(prev);
      newPairings.set(expectedId, actualItem);
      return newPairings;
    });
  };

  const handleUnpair = (expectedId: string) => {
    setManualPairings(prev => {
      const newPairings = new Map(prev);
      newPairings.delete(expectedId);
      return newPairings;
    });
  };

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd} collisionDetection={pointerWithin}>
      <div className="results-view">
        <section className="results-section">
          <h2>✅ Matched Expenses ({results.matched.length})</h2>
          {results.matched.length === 0 ? (
            <p className="empty-message">No matches found</p>
          ) : (
            results.matched.map((match, index) => (
              <div key={index} className="match-pair">
                <div className="expected">
                  <h4>Expected</h4>
                  <p className="inline-info">
                    <strong>Date:</strong> {match.expected.date} | <strong>Vendor:</strong> {match.expected.vendor} | <strong>Price:</strong> ${match.expected.price.toFixed(2)}
                  </p>
                </div>
                <div className="actual">
                  <h4>Actual</h4>
                  <p className="inline-info">
                    <strong>Date:</strong> {match.actual.date} | <strong>Vendor:</strong> {match.actual.vendor} | <strong>Price:</strong> ${match.actual.price.toFixed(2)}
                  </p>
                  <p><strong>Description:</strong> {match.actual.description}</p>
                  <p><strong>Activity:</strong> {match.actual.activity}</p>
                  {(match.actual.receipts.length > 0 || match.actual.needsAffidavit) && (
                    <p>
                      <strong>Receipts:</strong>{' '}
                      {match.actual.receipts.map((receipt, i) => (
                        <span key={i}>
                          {i > 0 && ', '}
                          <a href={receipt} target="_blank" rel="noopener noreferrer">
                            Receipt {i + 1}
                          </a>
                        </span>
                      ))}
                      {match.actual.needsAffidavit && (
                        <span>
                          {match.actual.receipts.length > 0 && ', '}
                          <a
                            href="#"
                            onClick={(e) => {
                              e.preventDefault();
                              handleDownloadAffidavit(match.expected);
                            }}
                            style={{ cursor: 'pointer' }}
                          >
                            Download Affidavit
                          </a>
                        </span>
                      )}
                    </p>
                  )}
                  {match.actual.flyer && (
                    <p>
                      <strong>Flyer:</strong>{' '}
                      <a href={match.actual.flyer} target="_blank" rel="noopener noreferrer">
                        View Flyer
                      </a>
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
        </section>

        <section className="results-section">
          <h2>⚠️ Missing Expected Expenses ({results.unmatched_expected.length})</h2>
          {results.unmatched_expected.length === 0 ? (
            <p className="success-message">All expected expenses matched!</p>
          ) : (
            <div className="missing-expenses-container">
              {results.unmatched_expected.map((exp, index) => {
                const expectedId = getExpectedId(exp, index);
                const pairedActual = manualPairings.get(expectedId);

                return (
                  <div key={expectedId} className="match-pair">
                    {/* Expected card (left side) */}
                    <div className="expected">
                      <h4>Expected</h4>
                      <p className="inline-info">
                        <strong>Date:</strong> {exp.date} | <strong>Vendor:</strong> {exp.vendor} | <strong>Price:</strong> ${exp.price.toFixed(2)}
                      </p>
                    </div>

                    {/* Drop zone (right side) */}
                    {pairedActual ? (
                      <div className="actual paired">
                        <button
                          className="unpair-button"
                          onClick={() => handleUnpair(expectedId)}
                          aria-label="Remove pairing"
                        >
                          ✕
                        </button>
                        <h4>Actual (Manual Match)</h4>
                        <p className="inline-info">
                          <strong>Date:</strong> {pairedActual.date} | <strong>Vendor:</strong> {pairedActual.vendor} | <strong>Price:</strong> ${pairedActual.price.toFixed(2)}
                        </p>
                        <p><strong>Description:</strong> {pairedActual.description}</p>
                        <p><strong>Activity:</strong> {pairedActual.activity}</p>
                        {(pairedActual.receipts.length > 0 || pairedActual.needsAffidavit) && (
                          <p>
                            <strong>Receipts:</strong>{' '}
                            {pairedActual.receipts.map((receipt, i) => (
                              <span key={i}>
                                {i > 0 && ', '}
                                <a href={receipt} target="_blank" rel="noopener noreferrer">
                                  Receipt {i + 1}
                                </a>
                              </span>
                            ))}
                            {pairedActual.needsAffidavit && (
                              <span>
                                {pairedActual.receipts.length > 0 && ', '}
                                Needs Affidavit
                              </span>
                            )}
                          </p>
                        )}
                        {pairedActual.flyer && (
                          <p>
                            <strong>Flyer:</strong>{' '}
                            <a href={pairedActual.flyer} target="_blank" rel="noopener noreferrer">
                              View Flyer
                            </a>
                          </p>
                        )}
                      </div>
                    ) : (
                      <DroppableZone id={expectedId}>
                        <div className="drop-placeholder">
                          Drop an expense here to match
                        </div>
                      </DroppableZone>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <section className="results-section">
          <h2>➕ Extra Actual Expenses ({availableActuals.length})</h2>
          {availableActuals.length === 0 ? (
            <p className="success-message">No extra expenses found!</p>
          ) : (
            <div className="extra-expenses-pool">
              {availableActuals.map(({ actual, originalIndex }) => {
                const actualId = getActualId(actual, originalIndex);

                return (
                  <DraggableActualCard
                    key={actualId}
                    id={actualId}
                    actual={actual}
                  />
                );
              })}
            </div>
          )}
        </section>
      </div>
    </DndContext>
  );
}
