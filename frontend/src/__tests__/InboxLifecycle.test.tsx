import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { InboxDashboard } from '@/components/InboxDashboard/InboxDashboard';
import type { InboxItem } from '@/types';

jest.mock('@/components/InboxDashboard/ResultsOverview', () => ({ ResultsOverview: () => <div>Results</div> }));
const visit: InboxItem = { id: 'one', session_id: 'visit-one', patient_pseudo: 'DEMO-TEST',
  created_at: '2026-11-08T12:00:00Z', status: 'reviewed', matches: [], approved_entities: ['asthma'] };

test('reviewed visit can be archived and restored without a delete action', async () => {
  const archive = jest.fn().mockResolvedValue(undefined);
  const { rerender } = render(<InboxDashboard items={[visit]} unreadCount={0} onMarkReviewed={jest.fn()} onArchive={archive} />);
  fireEvent.click(screen.getByRole('button', { name: /DEMO-TEST/ }));
  expect(screen.getByRole('link', { name: /View all visits/ })).toHaveAttribute('href', '/timeline?patient=DEMO-TEST');
  fireEvent.click(screen.getByRole('button', { name: 'Archive reviewed visit' }));
  await waitFor(() => expect(archive).toHaveBeenCalledWith('one', false));
  rerender(<InboxDashboard items={[{...visit, archived_at: '2026-11-08T13:00:00Z'}]} unreadCount={0} onMarkReviewed={jest.fn()} onArchive={archive} />);
  fireEvent.click(screen.getByRole('button', { name: 'Restore to inbox' }));
  await waitFor(() => expect(archive).toHaveBeenCalledWith('one', true));
});

test('archive failure is visible and leaves the action available for retry', async () => {
  render(<InboxDashboard items={[visit]} unreadCount={0} onMarkReviewed={jest.fn()} onArchive={jest.fn().mockRejectedValue(new Error('Connection lost'))} />);
  fireEvent.click(screen.getByRole('button', { name: /DEMO-TEST/ }));
  fireEvent.click(screen.getByRole('button', { name: 'Archive reviewed visit' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Connection lost');
  expect(screen.getByRole('button', { name: 'Archive reviewed visit' })).toBeEnabled();
});
