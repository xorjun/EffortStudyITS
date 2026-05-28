import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Observable } from 'rxjs';

export interface TaskStatusResponse {
  local_curriculum: string[];
  task_status_dict: { [taskName: string]: 'not attempted' | 'attempted' | 'completed' };
}

@Injectable({
  providedIn: 'root'
})
export class TaskStatusService {

  constructor(private client: HttpClient) {}

  getTaskStatus(courseUniqueName: string, topic: string): Observable<TaskStatusResponse> {
    const url = `${environment.apiUrl}/task/status/${courseUniqueName}/${topic}`;
    return this.client.get<TaskStatusResponse>(url, { withCredentials: true });
  }
}