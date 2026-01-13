import { Component, inject } from '@angular/core';
import { environment } from '../../environments/environment';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient, HttpEventType } from '@angular/common/http';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatCardModule, MatProgressBarModule, MatIconModule],
  templateUrl: './upload.html',
  styleUrls: ['./upload.css']
})
export class UploadComponent {
  selectedFile: File | null = null;
  isUploading = false;
  uploadProgress = 0;
  uploadResult: { filename: string, size: number, message: string } | null = null;
  private http = inject(HttpClient);

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.uploadProgress = 0;
      this.uploadResult = null;
    }
  }

  uploadFile() {
    if (!this.selectedFile) return;

    this.isUploading = true;
    this.uploadProgress = 0;
    this.uploadResult = null;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post<any>(`${environment.apiUrl}/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: (event) => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * event.loaded / event.total);
        } else if (event.type === HttpEventType.Response) {
          this.isUploading = false;
          this.uploadResult = event.body;
          this.selectedFile = null;
          this.uploadProgress = 0;
          console.log('Upload response:', event.body);
        }
      },
      error: (err) => {
        console.error('Upload failed', err);
        this.isUploading = false;
        alert('Upload failed: ' + err.message);
      }
    });
  }
}
