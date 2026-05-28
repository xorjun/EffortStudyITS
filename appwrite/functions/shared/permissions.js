import { ADMIN_TEAM_ID } from './constants.js';
import { Permission, Role } from './sdk.js';

export function participantDocumentPermissions(userId) {
  return [
    Permission.read(Role.user(userId)),
    Permission.update(Role.user(userId)),
    Permission.delete(Role.user(userId)),
    Permission.read(Role.team(ADMIN_TEAM_ID)),
    Permission.update(Role.team(ADMIN_TEAM_ID)),
    Permission.delete(Role.team(ADMIN_TEAM_ID)),
  ];
}

export function participantReadOnlyFilePermissions(userId) {
  return [
    Permission.read(Role.user(userId)),
    Permission.read(Role.team(ADMIN_TEAM_ID)),
    Permission.delete(Role.team(ADMIN_TEAM_ID)),
  ];
}

export function adminTeamDocumentPermissions() {
  return [
    Permission.read(Role.team(ADMIN_TEAM_ID)),
    Permission.update(Role.team(ADMIN_TEAM_ID)),
    Permission.delete(Role.team(ADMIN_TEAM_ID)),
  ];
}
