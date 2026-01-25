import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Auth, signOut } from '@angular/fire/auth';
import { Router } from '@angular/router';
import { UploadComponent } from '../upload/upload';
import { ChatComponent } from '../chat/chat';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    UploadComponent,
    ChatComponent
  ],
  template: `
    <div class="home-container">
      <mat-toolbar color="primary">
        <span>Secure RAG Demo</span>
        <span class="spacer"></span>
        <button mat-icon-button (click)="logout()" title="Logout">
          <mat-icon>logout</mat-icon>
        </button>
      </mat-toolbar>

      <div class="content">
        <div class="panel upload-panel">
          <app-upload></app-upload>
        </div>
        <div class="panel chat-panel">
          <app-chat></app-chat>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .home-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .content {
      display: flex;
      flex: 1;
      padding: 20px;
      gap: 20px;
      overflow: hidden;
      background-color: #f5f5f5;
    }
    .panel {
      flex: 1;
      background: white;
      border-radius: 8px;
      padding: 16px;
      overflow-y: auto;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Mobile responsive */
    @media (max-width: 768px) {
      .content {
        flex-direction: column;
      }
    }
  `]
})
export class HomeComponent {
  private auth: Auth = inject(Auth);
  private router: Router = inject(Router);

  async logout() {
    await signOut(this.auth);
    this.router.navigate(['/login']);
  }
}
