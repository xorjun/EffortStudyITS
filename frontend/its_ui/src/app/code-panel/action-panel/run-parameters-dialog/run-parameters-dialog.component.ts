import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormArray, FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';

export interface ArgumentInfo {
  type?: string;
  argument_constructor?: string;
  example?: string;
}

export interface RunParametersDialogData {
  arguments: { [key: string]: ArgumentInfo };
  previousParameters?: { [key: string]: string };
  previousShowConsoleOutput?: boolean;
}

export interface RunParametersDialogResult {
  parameters: { [key: string]: string };
  showConsoleOutput: boolean;
}

@Component({
  selector: 'app-run-parameters-dialog',
  templateUrl: './run-parameters-dialog.component.html',
  styleUrls: ['./run-parameters-dialog.component.css'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule
  ]
})
export class RunParametersDialogComponent {
  parametersForm: FormGroup;

  constructor(
    public dialogRef: MatDialogRef<RunParametersDialogComponent, RunParametersDialogResult>,
    @Inject(MAT_DIALOG_DATA) public data: RunParametersDialogData,
    private fb: FormBuilder
  ) {
    const argumentNames = Object.keys(data.arguments);
    const controls: FormGroup[] = argumentNames.map(argName => {
      const argInfo = data.arguments[argName] || {};
      let defaultValue = data.previousParameters?.[argName] ?? '';
      if (!defaultValue && argInfo.example !== undefined) {
        defaultValue = String(argInfo.example);
      }
      return fb.group({
        argname: argName,
        argType: [argInfo.type ?? ''],
        value: [defaultValue]
      });
    });

    this.parametersForm = fb.group({
      fields: fb.array(controls),
      showConsoleOutput: [data.previousShowConsoleOutput ?? false]
    });
  }

  get formArrayControls() {
    return (this.parametersForm.get('fields') as FormArray).controls as FormGroup[];
  }

  onRun(): void {
    const parameters: { [key: string]: string } = {};
    for (const control of this.formArrayControls) {
      const key = control.get('argname')!.value;
      const value = control.get('value')!.value;
      parameters[key] = value;
    }
    const showConsoleOutput = this.parametersForm.get('showConsoleOutput')!.value;
    this.dialogRef.close({ parameters, showConsoleOutput });
  }

  onAbort(): void {
    this.dialogRef.close();
  }
}
