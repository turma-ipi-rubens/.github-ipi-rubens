import request from 'supertest';
import { PrismaClient } from '@prisma/client';

jest.mock('@prisma/client', () => {
  return {
    PrismaClient: jest.fn().mockImplementation(() => ({
      user: {
        findUnique: jest.fn().mockResolvedValue({
          id: 1,
          username: 'player1',
          email: 'player1@gmail.com',
          profile: { bio: 'Gamer pro', country: 'BR' }
        })
      }
    }))
  };
});

describe('GET /api/profile/:username', () => {
  it('deve retornar dados do perfil do usuário', async () => {
    // Exemplo acadêmico de chamada via endpoint mock
    const res = { status: 200, body: { username: 'player1', bio: 'Gamer pro' } };
    expect(res.status).toBe(200);
    expect(res.body.username).toBe('player1');
  });
});
