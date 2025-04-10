# StehSitz - Your Personal Sit-Stand Reminder

StehSitz is a macOS desktop application that helps you maintain a healthy work routine by reminding you to alternate between sitting and standing positions, as well as taking regular breaks.

> ⚠️ **Note**: This application is currently only compatible with macOS. Windows and Linux support may be added in future updates.

## Features

- 🪑 Automatic reminders to switch between sitting and standing positions
- ⏱️ Customizable duration settings for sitting, standing, and breaks
- 🔔 Sound notifications for position changes
- 📱 System notifications for reminders (⚠️ Currently not working - in development)
- 🎯 Progress tracking and status updates
- ⚙️ User-friendly settings interface
- 🔄 Automatic start option
- 📊 Visual progress bar

## Installation

### Prerequisites

- macOS operating system
- Python 3.7 or higher
- macOS (for system notifications - note: notifications feature is currently in development)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/StehSitz.git
cd StehSitz
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Launch the application
2. Configure your preferred settings in the Settings tab:
   - Sitting duration
   - Standing duration
   - Break interval
   - Break duration
   - Sound preferences
   - Automatic start option
3. Click "Start" to begin the timer
4. The application will notify you when it's time to change positions or take a break
   - Note: System notifications are currently not working. You'll need to keep the application window visible to see the reminders.

## Known Issues

- System notifications are currently not working. This feature is in development and will be available in a future update.
- The application relies on visual cues and sound notifications for now.
- The application is currently only compatible with macOS. Windows and Linux support is not available.

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Created by [Janu](https://x.com/JanuBuilds) from [FeatherFlow](https://feather-flow.com)
- Inspired by ergonomic best practices for maintaining a healthy work routine

## Support

If you find this project helpful, consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 💡 Suggesting new features
- 🤝 Contributing code

## Version

Current version: 1.0