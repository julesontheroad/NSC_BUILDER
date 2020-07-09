using System.Diagnostics;
using System.IO;

namespace NSCB
{
    class Program
    {
        static void Main(string[] args)
        {
            string folderpath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().CodeBase);
            folderpath = folderpath.Replace(@"file:\", "");
            string nscbpath = Path.Combine(folderpath, "NSCB.bat");
            try
            {
                if (args.Length == 0)
                {
                    using (Process process = new Process())
                    {
                        ProcessStartInfo processStartInfo = new ProcessStartInfo();
                        processStartInfo.RedirectStandardOutput = false;
                        processStartInfo.UseShellExecute = false;
                        process.StartInfo = processStartInfo;
                        process.StartInfo.FileName = nscbpath;
                        process.Start();
                        process.WaitForExit();
                    }
                }
                else {
                    using (Process process = new Process())
                    {
                        string argos = '"' + (string)args[0] + '"';
                        ProcessStartInfo processStartInfo = new ProcessStartInfo();
                        processStartInfo.RedirectStandardOutput = false;
                        processStartInfo.UseShellExecute = false;
                        processStartInfo.Arguments = argos;
                        process.StartInfo = processStartInfo;
                        process.StartInfo.FileName = nscbpath;
                        process.Start();
                        process.WaitForExit();
                    }
                }
            }
            catch { }
        }
    }
}
