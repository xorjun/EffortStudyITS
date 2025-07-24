import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  configUrl = ''

  constructor(private http: HttpClient) {}

  // get method
  getConfig() {
    return this.http.get(this.configUrl)
  }
  
}
