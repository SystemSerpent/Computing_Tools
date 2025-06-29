using System;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace AsciiImageConverter
{
    public partial class MainForm : Form
    {
        private readonly string asciiChars = "@%#*+=-:. "; // From dark to light

        public MainForm()
        {
            InitializeComponent();
            // Setup form controls
            this.Text = "ASCII Image Converter";
            this.Width = 800;
            this.Height = 600;

            var loadButton = new Button { Text = "Load Image", Left = 10, Top = 10, Width = 100 };
            loadButton.Click += LoadButton_Click;
            this.Controls.Add(loadButton);

            var saveButton = new Button { Text = "Save ASCII", Left = 120, Top = 10, Width = 100 };
            saveButton.Click += SaveButton_Click;
            this.Controls.Add(saveButton);

            asciiTextBox = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Both,
                Left = 10,
                Top = 50,
                Width = this.ClientSize.Width - 20,
                Height = this.ClientSize.Height - 60,
                Font = new Font("Consolas", 6),
                WordWrap = false,
                ReadOnly = true
            };
            this.Controls.Add(asciiTextBox);
            this.Resize += (s, e) =>
            {
                asciiTextBox.Width = this.ClientSize.Width - 20;
                asciiTextBox.Height = this.ClientSize.Height - 60;
            };
        }

        private TextBox asciiTextBox;
        private Bitmap loadedImage;

        private void LoadButton_Click(object sender, EventArgs e)
        {
            using var dlg = new OpenFileDialog();
            dlg.Filter = "Image Files|*.bmp;*.jpg;*.jpeg;*.png;*.gif|All files|*.*";
            if (dlg.ShowDialog() == DialogResult.OK)
            {
                try
                {
                    loadedImage?.Dispose();
                    loadedImage = new Bitmap(dlg.FileName);
                    string asciiArt = ConvertToAscii(loadedImage, asciiTextBox.Width / 6); // approximate char width
                    asciiTextBox.Text = asciiArt;
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading image:\n{ex.Message}");
                }
            }
        }

        private void SaveButton_Click(object sender, EventArgs e)
        {
            using var dlg = new SaveFileDialog();
            dlg.Filter = "Text Files|*.txt";
            if (dlg.ShowDialog() == DialogResult.OK)
            {
                try
                {
                    System.IO.File.WriteAllText(dlg.FileName, asciiTextBox.Text);
                    MessageBox.Show("ASCII art saved!");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving file:\n{ex.Message}");
                }
            }
        }

        private string ConvertToAscii(Bitmap image, int maxWidth)
        {
            // Resize image to maxWidth while keeping aspect ratio
            int newWidth = maxWidth;
            int newHeight = (int)(image.Height / (double)image.Width * newWidth * 0.5); // adjust height for char aspect ratio
            var resized = new Bitmap(image, new Size(newWidth, newHeight));

            var sb = new StringBuilder();

            for (int y = 0; y < resized.Height; y++)
            {
                for (int x = 0; x < resized.Width; x++)
                {
                    Color pixel = resized.GetPixel(x, y);
                    int brightness = (int)((pixel.R + pixel.G + pixel.B) / 3);
                    int charIndex = brightness * (asciiChars.Length - 1) / 255;
                    sb.Append(asciiChars[charIndex]);
                }
                sb.AppendLine();
            }
            resized.Dispose();
            return sb.ToString();
        }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.Run(new MainForm());
        }
    }
}
