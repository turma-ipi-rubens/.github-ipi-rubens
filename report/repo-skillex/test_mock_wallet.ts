import { describe, it, expect, vi } from 'vitest';

describe('Carteira Fictícia (Mock)', () => {
  it('deve adicionar saldo corretamente na carteira virtual', () => {
    const carteira = { saldo: 100 };
    carteira.saldo += 50;
    expect(carteira.saldo).toBe(150);
  });
});
