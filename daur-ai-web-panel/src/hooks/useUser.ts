import { useState } from 'react';

// Minimal useUser hook stub returning a fake local user for the UI
export function useUser() {
  const [user] = useState(() => ({
    username: 'localuser',
    email: 'local@localhost',
    subscription: { tier: 'Free', requests: 0, storage: '0MB' }
  }));

  return { user };
}
