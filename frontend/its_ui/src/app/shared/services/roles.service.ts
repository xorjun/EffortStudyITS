import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})

export class RolesService {

    roles: any;

    constructor(private client: HttpClient) { 
      if (sessionStorage.getItem("courseName") != undefined)
        {
          this.fetchRoles();
        }
    }

    fetchRoles(): Observable<any> {
      const courseID = sessionStorage.getItem("courseID");
      const url = `${environment.apiUrl}/users/me`;
      return this.client.get(url, { withCredentials: true });
    }

    // Additional method to set course after fetching
    getRoles(): Observable<any> {
      return this.fetchRoles().pipe(
        tap(data => this.roles = data.roles)
      );
    }

}

