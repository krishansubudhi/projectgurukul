import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import React, { ReactNode } from "react"
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faWhatsapp, faXTwitter, faFacebook } from '@fortawesome/free-brands-svg-icons';
import { faCopy } from '@fortawesome/free-solid-svg-icons';
import './styles.css'; 


class SocialShareWidget extends StreamlitComponentBase {
  private title: string;
  private text: string;
  private url: string;

  constructor(props: any) {
    super(props);
    this.text = props.args['text'];
    this.url = props.args['url'];
    this.title = props.args['title'];
  }

  private formatMarkdown(): string {
    return `${this.title}\n\n${this.text}\n\n${this.url}`;
  }

  private formatTwitterText(): string {
    // Combine title, text, and URL
    const fullText = `${this.title}\n\n${this.text}\n\n${this.url}`;
  
    // Check if the length exceeds Twitter's character limit
    const maxLength = 280; // Twitter's character limit
    if (fullText.length > maxLength) {
      // Calculate the available space for the URL
      const availableSpaceForText = maxLength - this.url.length - "#projectgurukul".length -1;
  
      // Truncate the text and add ellipsis, leaving space for the URL
      const truncatedText = fullText.substring(0, availableSpaceForText - 4) + '...';
  
      // Combine the truncated text with the URL
      return `${truncatedText} ${this.url}`;
    }
  
    return fullText;
  }

  private shareOnWhatsApp = () => {
    const formattedMessage = encodeURIComponent(this.formatMarkdown());
    window.open(`whatsapp://send?text=${formattedMessage}`);
  };

  private shareOnTwitter = () => {
    const formattedMessage = encodeURIComponent(this.formatTwitterText());
    window.open(`https://twitter.com/intent/tweet?hashtags=projectgurukul&text=${formattedMessage}`);
  };

  private shareOnFacebook = () => {
    const formattedMessage = encodeURIComponent(this.formatMarkdown());
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${formattedMessage}`);
  };

  private copyToClipboard = () => {
    const formattedText = this.formatMarkdown();
  
    // Check if navigator.clipboard.writeText is supported
    if (navigator.clipboard && navigator.clipboard.writeText) {
      // Use the modern clipboard API
      navigator.clipboard.writeText(formattedText).then(
        () => {
          console.log('Text copied to clipboard:', formattedText);
          Streamlit.setComponentValue('copy');
        },
        (err) => console.error('Unable to copy to clipboard', err)
      );
    } else {
      // Fallback to the document.execCommand approach with a textarea
      const tempInput = document.createElement('textarea');
      tempInput.value = formattedText;
      document.body.appendChild(tempInput);
  
      tempInput.select();
      tempInput.setSelectionRange(0, 99999); // For mobile devices
  
      document.execCommand('copy');
  
      document.body.removeChild(tempInput);
  
      console.log('Text copied to clipboard:', formattedText);
      Streamlit.setComponentValue('copy');
    }
  };
  
  

  public render = (): ReactNode => {
    return (
      <span className="social-share-container">
        <button className="icon-button" onClick={this.shareOnWhatsApp}>
          <FontAwesomeIcon icon={faWhatsapp} />
        </button>

        <button className="icon-button" onClick={this.shareOnTwitter}>
          <FontAwesomeIcon icon={faXTwitter} />
        </button>

        <button className="icon-button" onClick={this.shareOnFacebook}>
          <FontAwesomeIcon icon={faFacebook} />
        </button>

        <button className="icon-button" onClick={this.copyToClipboard}>
          <FontAwesomeIcon icon={faCopy} />
        </button>
      </span>
    );
  };
}

export default withStreamlitConnection(SocialShareWidget);
