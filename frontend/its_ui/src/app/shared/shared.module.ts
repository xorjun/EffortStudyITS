import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';
import { MarkdownPanelComponent } from './components/markdown-panel/markdown-panel.component';
import { DataTermsPopupComponent } from './components/data-terms-popup/data-terms-popup.component';
import { MonacoCodeEditorComponent } from './components/monaco-code-editor/monaco-code-editor.component';
import { PrivacyPolicyPopupComponent } from './components/privacy-policy-popup/privacy-policy-popup.component';
import { ImprintPopupComponent } from './components/imprint-popup/imprint-popup.component';


@NgModule({
  declarations: [MarkdownPanelComponent, DataTermsPopupComponent, MonacoCodeEditorComponent, PrivacyPolicyPopupComponent, ImprintPopupComponent],
  imports: [
    CommonModule,
    MarkdownModule.forChild(),
    // ReactiveFormsModule
  ],
  exports: [MarkdownPanelComponent, DataTermsPopupComponent, MonacoCodeEditorComponent, PrivacyPolicyPopupComponent, ImprintPopupComponent]
})
export class SharedModule {}
