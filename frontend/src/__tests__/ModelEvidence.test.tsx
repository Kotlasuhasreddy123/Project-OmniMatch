import { render, screen } from '@testing-library/react';
import { ModelEvidence } from '@/components/ModelEvidence';

test('model results distinguish development recall from candidate accuracy and the unmet target', () => {
  render(<ModelEvidence />);
  expect(screen.getByText('90.0% internal context accuracy')).toBeInTheDocument();
  expect(screen.getByText(/54 of 60 supplied term spans/)).toBeInTheDocument();
  expect(screen.getByText(/98% minimum: not achieved/)).toBeInTheDocument();
  expect(screen.getByText(/The broad 95% recall target is still unmet/)).toBeInTheDocument();
  expect(screen.getByText(/Only 1 family-history test example/)).toBeInTheDocument();
});
