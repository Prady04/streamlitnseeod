
var ab = WScript.CreateObject("Broker.Application");
ab.Visible = true;
var fmt = "nse.format"
var x = ab.Import(0,"C:\\Trading Stuff\\bhavcopy\\fno\\06062022_NSE.txt", "nsepy.format");
WScript.Echo(x)
ab.RefreshAll();
ab.SaveDatabase();
ab.Quit();
WScript.Echo("success")

