import api from './api';
import type { User } from './auth';

export interface Team {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  is_active: boolean;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  is_leader: boolean;
  joined_at: string;
}

export interface TeamMemberWithUser extends TeamMember {
  user: User;
}

export interface TeamDetail extends Team {
  members: TeamMemberWithUser[];
}

export interface TeamCreateParams {
  name: string;
  description?: string;
}

export interface TeamUpdateParams {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface TeamMemberCreateParams {
  user_id: number;
  is_leader?: boolean;
}

export const getTeams = async (params?: { is_active?: boolean }): Promise<Team[]> => {
  const response = await api.get('/teams/', { params });
  return response as Team[];
};

export const getTeam = async (id: number): Promise<TeamDetail> => {
  const response = await api.get(`/teams/${id}`);
  return response as TeamDetail;
};

export const createTeam = async (params: TeamCreateParams): Promise<Team> => {
  const response = await api.post('/teams/', params);
  return response as Team;
};

export const updateTeam = async (id: number, params: TeamUpdateParams): Promise<Team> => {
  const response = await api.put(`/teams/${id}`, params);
  return response as Team;
};

export const deleteTeam = async (id: number): Promise<void> => {
  await api.delete(`/teams/${id}`);
};

export const addTeamMember = async (teamId: number, params: TeamMemberCreateParams): Promise<TeamDetail> => {
  const response = await api.post(`/teams/${teamId}/members/`, params);
  return response as TeamDetail;
};

export const removeTeamMember = async (teamId: number, userId: number): Promise<void> => {
  await api.delete(`/teams/${teamId}/members/${userId}`);
};
