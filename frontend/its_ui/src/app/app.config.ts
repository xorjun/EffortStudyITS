import { APP_INITIALIZER, ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { ReactiveFormsModule } from '@angular/forms';
import { MarkdownModule, MARKED_OPTIONS } from 'ngx-markdown';
import { StarRatingModule } from 'angular-star-rating';
import { DatePipe } from '@angular/common';
import { MAT_TOOLTIP_DEFAULT_OPTIONS, MatTooltipDefaultOptions } from '@angular/material/tooltip';
import { RuntimeConfigService } from './shared/services/runtime-config.service';

const tooltipDefaults: MatTooltipDefaultOptions = {
  showDelay: 500,
  hideDelay: 0,
  touchendHideDelay: 1500,
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptorsFromDi()),
    provideAnimations(),
    DatePipe,
    { provide: MAT_TOOLTIP_DEFAULT_OPTIONS, useValue: tooltipDefaults },
    {
      provide: APP_INITIALIZER,
      useFactory: (runtimeConfigService: RuntimeConfigService) => () => runtimeConfigService.load(),
      deps: [RuntimeConfigService],
      multi: true,
    },
    importProvidersFrom(
      ReactiveFormsModule,
      StarRatingModule.forRoot(),
      MarkdownModule.forRoot({
        markedOptions: {
          provide: MARKED_OPTIONS,
          useValue: {
            gfm: false
          },
        },
      })
    )
  ]
};
