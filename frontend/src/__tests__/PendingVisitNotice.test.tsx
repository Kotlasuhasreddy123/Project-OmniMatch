import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { PendingVisitNotice } from '@/components/InboxDashboard/PendingVisitNotice';
import { completeSession } from '@/lib/apiClient';
import type { InboxItem } from '@/types';

jest.mock('@/lib/apiClient', () => ({ completeSession: jest.fn() }));
jest.mock('@/lib/auth', () => ({ getCurrentUser: () => ({ sub: 'user-a' }) }));
const approved=[{term:'asthma',entity_type:'DISEASE',confidence:.9,status:'approved',context:'patient',negated:false}];
function save(age=0,extra={}) {
  sessionStorage.setItem('omni_pending_visit',JSON.stringify({sessionId:'visit-a',patientLabel:'DEMO-TEST',
    submittedAt:Date.now()-age,ownerId:'user-a',approvedEntities:approved,evidenceSpans:[],...extra}));
}
beforeEach(() => { sessionStorage.clear(); jest.clearAllMocks(); });
afterEach(() => { jest.useRealTimers(); });

test('shows pending processing without automatically resubmitting', () => {
  save();render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  expect(screen.getByRole('status')).toHaveTextContent('being processed');
  expect(screen.queryByRole('button',{name:'Retry checked visit'})).not.toBeInTheDocument();
  expect(completeSession).not.toHaveBeenCalled();
});
test('delivery target warning appears when sixty seconds pass', () => {
  jest.useFakeTimers();save();render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  act(() => { jest.advanceTimersByTime(60_000); });
  expect(screen.getByRole('alert')).toHaveTextContent('does not mean that no studies were found');
  expect(screen.getByRole('button',{name:'Retry checked visit'})).toBeEnabled();
});
test('successful inbox delivery clears pending state', () => {
  save();render(<PendingVisitNotice items={[{session_id:'visit-a'} as InboxItem]} onRefresh={jest.fn()} />);
  expect(screen.queryByRole('status')).not.toBeInTheDocument();
  expect(sessionStorage.getItem('omni_pending_visit')).toBeNull();
});
test('explicit retry submits only the previously reviewed payload', async () => {
  (completeSession as jest.Mock).mockResolvedValue({});save(70_000);const refresh=jest.fn().mockResolvedValue(undefined);
  render(<PendingVisitNotice items={[]} onRefresh={refresh} />);
  expect(completeSession).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Retry checked visit'}));
  await waitFor(() => expect(refresh).toHaveBeenCalledTimes(1));
  expect(completeSession).toHaveBeenCalledWith('visit-a',approved,[],'DEMO-TEST');
  expect(screen.getByRole('status')).toHaveTextContent('being processed');
});
test('retry failure remains visible and allows a later retry', async () => {
  (completeSession as jest.Mock).mockRejectedValue(new Error('Service temporarily unavailable'));save(70_000);
  render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  fireEvent.click(screen.getByRole('button',{name:'Retry checked visit'}));
  expect(await screen.findByText('Service temporarily unavailable')).toBeVisible();
  expect(screen.getByRole('button',{name:'Retry checked visit'})).toBeEnabled();
  expect(sessionStorage.getItem('omni_pending_visit')).not.toBeNull();
});
test('a different account cannot display or retry the pending visit', () => {
  save(70_000,{ownerId:'other-account'});render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  expect(screen.queryByText(/DEMO-TEST/)).not.toBeInTheDocument();
  expect(sessionStorage.getItem('omni_pending_visit')).toBeNull();
  expect(completeSession).not.toHaveBeenCalled();
});
test('malformed browser state is discarded safely', () => {
  sessionStorage.setItem('omni_pending_visit','not-json');render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  expect(sessionStorage.getItem('omni_pending_visit')).toBeNull();
});
test('an older marker without a reviewed payload allows refresh but no retry', () => {
  save(70_000,{approvedEntities:undefined});render(<PendingVisitNotice items={[]} onRefresh={jest.fn()} />);
  expect(screen.getByRole('button',{name:'Refresh inbox'})).toBeEnabled();
  expect(screen.queryByRole('button',{name:'Retry checked visit'})).not.toBeInTheDocument();
});
