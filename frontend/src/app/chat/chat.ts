import { Component, inject } from '@angular/core';
import { environment } from '../../environments/environment';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

interface ChatMessage {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    FormsModule
  ],
  template: `
    <div class="chat-container">
      <h3>AI Assistant</h3>
      <div class="messages">
        <div *ngFor="let msg of messages" class="message" [ngClass]="{'user': msg.isUser, 'bot': !msg.isUser}">
          <div class="bubble">{{ msg.text }}</div>
        </div>
      </div>
      <div class="input-area">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Ask a question...</mat-label>
          <input matInput [(ngModel)]="newMessage" (keyup.enter)="sendMessage()">
          <button mat-icon-button matSuffix (click)="sendMessage()" [disabled]="!newMessage.trim()">
            <mat-icon>send</mat-icon>
          </button>
        </mat-form-field>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .message {
      display: flex;
    }
    .message.user {
      justify-content: flex-end;
    }
    .message.bot {
      justify-content: flex-start;
    }
    .bubble {
      padding: 10px 15px;
      border-radius: 18px;
      max-width: 80%;
      word-wrap: break-word;
    }
    .user .bubble {
      background-color: #3f51b5;
      color: white;
      border-bottom-right-radius: 4px;
    }
    .bot .bubble {
      background-color: #e0e0e0;
      color: black;
      border-bottom-left-radius: 4px;
    }
    .input-area {
      padding-top: 10px;
    }
    .full-width {
      width: 100%;
    }
  `]
})
export class ChatComponent {
  messages: ChatMessage[] = [
    { text: 'Hello! Upload a document to start chatting.', isUser: false, timestamp: new Date() }
  ];
  newMessage = '';
  private http = inject(HttpClient);

  async sendMessage() {
    if (!this.newMessage.trim()) return;

    // Add user message
    const userMsg: ChatMessage = { text: this.newMessage, isUser: true, timestamp: new Date() };
    this.messages.push(userMsg);

    const messageToSend = this.newMessage;
    this.newMessage = ''; // Clear input immediately

    // Add placeholder bot message
    const botMsg: ChatMessage = { text: 'Thinking...', isUser: false, timestamp: new Date() };
    this.messages.push(botMsg);

    try {
      const response = await firstValueFrom(this.http.post<any>(`${environment.apiUrl}/chat`, {
        message: messageToSend
      }));

      // Update bot message
      botMsg.text = response.response;
    } catch (error) {
      console.error('Chat error:', error);
      botMsg.text = "Sorry, I encountered an error. Please try again.";
    }
  }
}
