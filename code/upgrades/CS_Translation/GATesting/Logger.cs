using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace GATesting
{

    public enum LogLevel
    {
        Debug, Info, Warning, Error, Critical
    }

    public class Log
    {
        private readonly uint _logicClockStamp;
        private readonly DateTime _timeStamp;
        private readonly string _message;
        private readonly LogLevel _level;

        public string Message { get => _message;}
        public LogLevel Level { get => _level;}
        public uint LogicClockStamp { get => _logicClockStamp; }
        public DateTime TimeStamp { get => _timeStamp; }

        internal Log(string message, LogLevel level, uint logicClock, DateTime timeStamp) 
        {
            _message = message;
            _level = level;
            _logicClockStamp = logicClock;
            _timeStamp = timeStamp;
        }

        public string ToString()
        {
            return _logicClockStamp.ToString() + ": " + _level.ToString() + " - " + _message + " at " + _timeStamp.ToString();
        }

        public Log Copy()
        {
            return new Log(_message, _level, _logicClockStamp, _timeStamp);
        }
    }

    public class Logger
    {

        public static Logger INSTANCE = new Logger();

        public static Logger Instance { get { 
                if (INSTANCE == null)
                {
                    INSTANCE = new Logger();
                }
                return INSTANCE; 
            } }

        public uint LogicClock { get => _logicClock; }

        private Dictionary<LogLevel, ConsoleColor> _colors;

        private List<Log> _logs;
        private uint _logicClock;

        private Logger()
        {
            _logs = new List<Log>();
            _logicClock = 0;
            _colors = new Dictionary<LogLevel, ConsoleColor>
            {
                { LogLevel.Debug, ConsoleColor.Gray },
                { LogLevel.Info, ConsoleColor.White },
                { LogLevel.Warning, ConsoleColor.Yellow },
                { LogLevel.Error, ConsoleColor.Red },
                { LogLevel.Critical, ConsoleColor.Cyan }
            };
        }

        public void Log(string message, LogLevel level)
        {
            _logs.Add(new Log(message, level, _logicClock++, DateTime.Now));
        }

        public void Reset()
        {
            _logicClock = 0;
            _logs.Clear();
        }

        public void ToFile(string path)
        {
            string text = JsonConvert.SerializeObject(this);
            File.AppendAllText(@path, text);
        }

        public void Load(string path)
        {
            Reset();
            using (StreamReader r = new StreamReader(path))
            {
                string json = r.ReadToEnd();
                _logs = JsonConvert.DeserializeObject<List<Log>>(json);
                _logicClock = _logs.Last().LogicClockStamp + 1;
            }
        }

        public Log GetLog(int logicClock)
        {
            return _logs.FirstOrDefault(x => x.LogicClockStamp == logicClock);
        }

        public Log GetLog(DateTime timeStamp)
        {
            return _logs.FirstOrDefault(x => x.TimeStamp.Equals(timeStamp));
        }

        public List<Log> GetByLevel(LogLevel level)
        {
            return _logs.FindAll(x => x.Level == level);
        }

        public List<Log> GetLogsBetween(uint logicClockStart = 0, uint logicClockEnd = 0)
        {
            if(logicClockEnd == 0)
            {
                logicClockEnd = _logs.Last().LogicClockStamp;
            }
            return _logs.FindAll(x => x.LogicClockStamp >= logicClockStart && x.LogicClockStamp <=  logicClockEnd);
        }

        public List<Log> GetLogsBetween(DateTime timeStampStart, DateTime timeStampEnd)
        {
            return _logs.FindAll(x => x.TimeStamp >= timeStampStart && x.TimeStamp<= timeStampEnd);
        }

        private void Print(List<Log> logs)
        {
            foreach (Log log in logs)
            {
                Console.ForegroundColor = _colors[log.Level];
                Console.WriteLine(log.ToString());
                Console.ResetColor();
            }
        }

        public void PrintLogs(uint logicClockStart = 0, uint logicClockEnd = 0)
        {
            List<Log> logs = GetLogsBetween(logicClockStart, logicClockEnd);
            Print(logs);
        }

        public void PrintLogs(DateTime timeStampStart, DateTime timeStampEnd)
        {
            List<Log> logs = GetLogsBetween(timeStampStart, timeStampEnd);
            Print(logs);
        }

        public void ChangePrintColor(LogLevel level, ConsoleColor color)
        {
            _colors[level] = color;
        }

        public int CountLevel(LogLevel level)
        {
            return _logs.FindAll(x => x.Level == level).Count();
        }

        public float GetLevelRate(LogLevel level)
        {
            return (float)CountLevel(level) / (float)_logs.Count();
        }

        public List<string> GetMessages(uint logicClockStart = 0, uint logicClockEnd = 0)
        {
            if (logicClockEnd == 0)
            {
                logicClockEnd = _logs.Last().LogicClockStamp;
            }
            List<string> messages = new List<string>();
            foreach(Log log in _logs.FindAll(x=> x.LogicClockStamp >= logicClockStart && x.LogicClockStamp <= logicClockEnd))
            {
                messages.Add(log.Message);
            }
            return messages;
        }

        public List<string> GetMessages(DateTime timeStampStart, DateTime timeStampEnd)
        {
            List<string> messages = new List<string>();
            foreach (Log log in _logs.FindAll(x => x.TimeStamp >= timeStampStart && x.TimeStamp <= timeStampEnd))
            {
                messages.Add(log.Message);
            }
            return messages;
        }

        public List<string> GetMessages(LogLevel level)
        {
            List<string> messages = new List<string>();
            foreach (Log log in _logs.FindAll(x=> x.Level == level))
            {
                messages.Add(log.Message);
            }
            return messages;
        }

        public Log GetLast()
        {
            return _logs.Last().Copy();
        }

        public Log GetFirst()
        {
            return _logs.First().Copy();
        }

    }
}
