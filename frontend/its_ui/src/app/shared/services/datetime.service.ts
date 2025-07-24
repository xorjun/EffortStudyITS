import { Injectable } from '@angular/core';
import { DatePipe } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class DatetimeService {

  constructor(public datePipe: DatePipe) { }

  datetimeNow() {
    const datetime_obj = {
      "local": this.datePipe.transform((new Date), 'dd.MM.yyyy HH:mm:ss'),
      "utc": this.datePipe.transform((new Date), 'dd.MM.yyyy HH:mm:ss', '+0:00'),
    };
    return datetime_obj
  }


  datetimeNowLocal(){
    const datetime_obj = {
      "local": this.datePipe.transform((new Date), 'dd.MM.yyyy HH:mm:ss.SSS'),
    };
    return datetime_obj
  }

  datetimeNowUTC(){
    const datetime_obj = {
      "utc": this.datePipe.transform((new Date), 'dd.MM.yyyy HH:mm:ss.SSS', '+0:00'),
    };
    return datetime_obj
  }

}
