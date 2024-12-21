#!/usr/bin/perl 

## --> Microwave Radio Path Analysis, path.main.cgi
## --> Green Bay Professional Packet Radio, www.gbppr.net

## This file Copyright 2003 <contact@gbppr.net> under the GPL
## NO WARRANTY. Please send bug reports / patches / reports.

## Program Setup
#
select STDOUT;
$| = 1;

## User Setup
#
my $pic     = "../pics/path.png";
my $example = "../pics/example/index.html";
my $form    = "./path.cgi";

## Print MIME
#
print "Content-type:text/html\n\n";

## Draw me a web page
#
print <<EOF;
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html>
<head>
<title>Microwave Radio Path Analysis</title>
</head>
<body bgcolor="#D3D3D3" text="#000000" link="blue">
<font face="Helvetica">

<center>
<table border="10" cellpadding="10">
<tr>
<td bgcolor="#A3A3A3"><font size="12" face="Helvetica" color="#82007C"><b>Microwave Radio Path Analysis</b></font></td>
</tr>

<tr>
<td bgcolor="#A3A3A3" align="center">A service of <a href="http://www.gbppr.net">GBPPR Radiation Laboratory</a></td>
</tr>
</table>
</center>

<center>
<p><a href="$example"><img src="$pic" border="0" height="480" width="640"></a><br><b><font color="red">EXPERIMENTAL - WORK IN PROGRESS - MAY GIVE WEIRD RESULTS</font></b></p>
</center>

<form action="$form" method="post">

<blockquote>
<table border="4" cellpadding="8">
<tr>
<td colspan="10" bgcolor="#7EBDE5"><font size="5"><b>Transmitter Site Information</b></font></td>
</tr>
</table>

<table border="1" width="100%">
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="0" width="75%">
<tr><td></td></tr>
<tr>
<td align="right"><b>Project Name</b></td>
<td><input type="text" name="project" size="30" value="Special Collection Service"></td>
<td></td>
</tr>

<tr>
<td align="right"><b>Site Name</b></td>
<td><input type="text" name="tx_name" size="15" value="TX"></td> 
<td></td>
</tr>

<tr>
<td align="right"><b>Equipment Model / Notes</b></td>
<td><input type="text" name="tx_notes" size="30" value="">
</tr>

<tr>
<td align="right"><b>Site Latitude</b></td>
<td><input type="number" name="LAT1_D" min="0" max="90" value="44" step="1">&nbsp;&deg;&nbsp;
<input type="number" name="LAT1_M" min="0" max="59" value="31" step="1">&nbsp;'&nbsp;
<input type="number" name="LAT1_S" min="0" max="59.99" value="37.00" step="0.01">&nbsp;"</td>
<td><input type="radio" name="LAT1_val" value="North" checked>North&nbsp;&nbsp;
<input type="radio" name="LAT1_val" value="South">&nbsp;South&nbsp;&nbsp;(WGS84)</td>
</tr>

<tr>
<td align="right"><b>Site Longitude</b></td>
<td><input type="number" name="LON1_D" min="0" max="180" value="88" step="1">&nbsp;&deg;&nbsp;
<input type="number" name="LON1_M" min="0" max="59" value="2" step="1">&nbsp;'&nbsp;
<input type="number" name="LON1_S" min="0" max="59.99" value="35.00" step="0.01">&nbsp;"</td>
<td><input type="radio" name="LON1_val" value="West" checked>West&nbsp;&nbsp;
<input type="radio" name="LON1_val" value="East">&nbsp;East&nbsp;&nbsp;(WGS84)</td>
</tr>

<tr>
<td align="right"><b>Highest Transmitted Frequency</b></td>
<td><input type="text" name="frq" size="5" value="2467">
<select name="frq_val">
<option selected>MHz</option>
<option>GHz</option>
</select></td>
<td>20 MHz to 20 GHz</td>
</tr>

<tr>
<td align="right" bgcolor="#BABBBE"><b>Diversity Frequency</b></td>
<td bgcolor="#BABBBE"><input type="text" name="frq_div" size="5" value="0">
<select name="frq_div_val">
<option selected>MHz</option>
<option>GHz</option>
</select></td>
<td bgcolor="#BABBBE">Leave "0" if unused</td>
</tr>

<tr>
<td align="right"><b>RF Power Output</b></td>
<td><input type="number" name="pwr_out" min="-99.0" max="9999.0" step="0.1" value="20.0">
<select name="pwr_out_val">
<option selected>dBm</option>
<option>milliwatts</option>
<option>watts</option>
<option>kilowatts</option>
<option>dBW</option>
<option>dBk</option>
</select></td>
<td></td>
</tr>

<tr>
<td align="right"><b>External Transmission Line Type</b></td>
<td><select name="tx_cab">
<option>Times Microwave LMR-200</option>
<option>Times Microwave LMR-240</option>
<option selected>Times Microwave LMR-400</option>
<option>Times Microwave LMR-400 UltraFlex</option>
<option>Times Microwave LMR-500</option>
<option>Times Microwave LMR-600</option>
<option>Times Microwave LMR-900</option>
<option>Times Microwave LMR-1200</option>
<option>Times Microwave LMR-1700</option>
<option>Andrew HELIAX EFX2-50</option>
<option>Andrew HELIAX LDF1-50</option>
<option>Andrew HELIAX LDF2-50</option>
<option>Andrew HELIAX LDF4-50A</option>
<option>Andrew HELIAX LDF4.5-50</option>
<option>Andrew HELIAX LDF5-50A</option>
<option>Andrew HELIAX LDF6-50A</option>
<option>Andrew HELIAX LDF7-50A</option>
<option>Andrew HELIAX LDF12-50</option>
<option>Andrew HELIAX FSJ1-50A</option>
<option>Andrew HELIAX FSJ2-50</option>
<option>Andrew HELIAX FSJ4-50B</option>
<option>Andrew HELIAX HT4-50</option>
<option>Andrew HELIAX HT5-50</option>
<option>Andrew HELIAX HST1-50</option>
<option>Andrew HELIAX HJ4-50</option>
<option>Andrew HELIAX HJ4.5-50</option>
<option>Andrew HELIAX HJ5-50</option>
<option>Andrew HELIAX HJ7-50A</option>
<option>Andrew HELIAX HJ12-50</option>
<option>Andrew HELIAX HJ8-50B</option>
<option>Andrew HELIAX HJ11-50</option>
<option>Andrew HELIAX HJ9-50</option>
<option>Andrew HELIAX VXL5-50</option>
<option>Andrew HELIAX VXL6-50</option>
<option>Andrew HELIAX VXL7-50</option>
<option>Andrew HELIAX EW17</option>
<option>Andrew HELIAX EWP17</option>
<option>Andrew HELIAX EW20</option>
<option>Andrew HELIAX EW28</option>
<option>Andrew HELIAX EW34</option>
<option>Andrew HELIAX EWP34</option>
<option>Andrew HELIAX EW37</option>
<option>Andrew HELIAX EWP37</option>
<option>Andrew HELIAX EWP37S</option>
<option>Andrew HELIAX EW44</option>
<option>Andrew HELIAX EWP44</option>
<option>Andrew HELIAX EWS44</option>
<option>Andrew HELIAX EW52</option>
<option>Andrew HELIAX EWP52</option>
<option>Andrew HELIAX EWP52S</option>
<option>Andrew HELIAX EW63</option>
<option>Andrew HELIAX EWP63</option>
<option>Andrew HELIAX EWP63S</option>
<option>Andrew HELIAX EW64</option>
<option>Andrew HELIAX EWP64</option>
<option>Andrew HELIAX EW77</option>
<option>Andrew HELIAX EWP77</option>
<option>Andrew HELIAX EW85</option>
<option>Andrew HELIAX EW90</option>
<option>Andrew HELIAX EWP90</option>
<option>Andrew HELIAX EWP90S</option>
<option>Andrew HELIAX EW127A</option>
<option>Andrew HELIAX EWP127A</option>
<option>Andrew HELIAX EW132</option>
<option>Andrew HELIAX EWP132</option>
<option>Andrew HELIAX EW180</option>
<option>Andrew HELIAX EWP180</option>
<option>Andrew HELIAX EW220</option>
<option>Andrew WR284</option>
<option>Andrew WR229</option>
<option>Andrew WR187</option>
<option>Andrew WR159</option>
<option>Andrew WR137</option>
<option>Andrew WR112</option>
<option>Andrew WR90</option>
<option>Andrew WR75</option>
<option>Andrew WR62</option>
<option>Andrew WR42</option>
<option>Belden 9913 (RG-8)</option>
<option>Belden 8237 (RG-8)</option>
<option>Belden 8267 (RG-213)</option>
<option>Belden 9258 (RG-8X)</option>
<option>Belden 8240 (RG-58)</option>
<option>M&P AIRBORNE 10</option>
<option>M&P BROAD PRO 50</option>
<option>Crap RG-8</option>
<option>Other</option>
</select>
</td><td></td>
</tr>

<tr>
<td bgcolor="#BABBBE" align="right"><b>If </b><font color="maroon">Other</font><b>, Enter Transmission Line Loss Specification</b></td>
<td bgcolor="#BABBBE"><input type="number" name="tx_cab_other" min="0.00" max="99.99" value="0.00" step="0.01"> dB</td>
<td bgcolor="#BABBBE">
<input type="radio" name="check1" value="feet" checked>&nbsp;per 100 feet&nbsp;&nbsp;
<input type="radio" name="check1" value="meters">&nbsp;per 100 meters
</td>
</tr>

<tr>
<td align="right"><b>External Transmission Line Length</b></td>
<td><input type="number" name="tx_len" min="1.0" max="999.9" value="55.0" step="0.1">
<select name="tx_len_val">
<option selected>feet</option>
<option>meters</option>
</select>
<td></td>
</tr>

<tr>
<td align="right"><b>Antenna Height (Center-of-Radiation)</b></td>
<td><input type="number" name="tx_ant_ht" min="1.0" max="2000.0" value="25.0" step="0.1">
<select name="tx_ant_ht_val">
<option selected>feet</option>
<option>meters</option></select>
<td>Above Ground Level</td>
</tr>

<tr>
<td align="right"><b>Antenna Peak Gain</b></td>
<td><input type="number" name="tx_ant_gain" min="0.0" max="60.0" value="24.0" step="0.1">
<select name="tx_ant_val">
<option selected>dBi</option>
<option>dBd</option>
</select>
&nbsp;&nbsp;Radome Loss <input type="number" name="tx_ant_gain_radome" min="0.00" max="3.00" value="0.00" step="0.01"> dB
<td>(Note 1)</td>
</tr>

<tr>
<td align="right"><b>Antenna Model / Notes</b></td>
<td><input type="text" name="tx_ant_notes" size="30" value="Conifer 24 dBi">
<td></td>
</tr>

<tr>
<td align="right"><b>Miscellaneous Transmission Line Losses</b></td>
<td><input type="number" name="tx_misc_cab_loss" min="0.00" max="99.99" value="0.00" step="0.01"> dB</td>
<td>
<select name="null">
<option selected>-- EXAMPLES --</option>
<option>2-Port Splitter&nbsp;&nbsp;(3.5 dB)</option>
<option>4-Port Splitter&nbsp;&nbsp;(6.5 dB)</option>
<option>PolyPhaser&nbsp;&nbsp;(0.2 dB)</option>
<option>Right-Angle N Adapter&nbsp;&nbsp;(0.5 dB)</option>
<option>RF Connector&nbsp;&nbsp;(0.15 dB)</option>
<option>DC Injector&nbsp;&nbsp;(0.2 dB)</option>
<option>Isolator&nbsp;&nbsp;(0.8 dB)</option>
<option>Filter&nbsp;&nbsp;(2 dB)</option>
<option>RF Branching Losses</option>
<option>Transmit-Only Attenuator Pad</option>
<option>Flexible Jumpers</option>
<option>Standby Switches</option>
<option>Antenna Coupling Unit</option>
</select>
</td>
</tr>

<tr>
<td align="right"><b>Miscellaneous Gains, After Line/Misc. Loss</b></td>
<td><input type="number" name="tx_misc_gain" min="0.0" max="60.0" value="0.0" step="0.1"> dB</td>
<td>
<select name="null">
<option selected>-- EXAMPLES --</option>
<option>Tower-Mounted Power Amplifier&nbsp;&nbsp;(20 dB)</option>
</select>
</td>
</tr>

<tr>
<td align="right"><b>Miscellaneous Path Losses</b></td>
<td><input type="number" name="tx_misc_loss" min="0.0" max="99.0" value="0.0" step="0.1"> dB</td>
<td>
<select name="null">
<option selected> -- EXAMPLES --</option>
<option>Tree Absorption&nbsp;&nbsp;(0.15-0.4 dB/meter @ 1 GHz)</option>
<option>Tree Absorption&nbsp;&nbsp;(0.25-0.5 dB/meter @ 2.4 GHz)</option>
<option>Tree Absorption&nbsp;&nbsp;(0.4-0.6 dB/meter @ 3.3 GHz)</option>
<option>Tree Absorption&nbsp;&nbsp;(0.5-1.5 dB/meter @ 5.8 GHz)</option>
<option>Tree Absorption&nbsp;&nbsp;(1.0-2.0 dB/meter @ 10 GHz)</option>
<option>Slight Antenna Misalignment Loss&nbsp;&nbsp;(0.5 dB)</option>
<option>90&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(20 dB)</option>
<option>75&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(12 dB)</option>
<option>60&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(6 dB)</option>
<option>45&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(3 dB)</option>
<option>30&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(1.3 dB)</option>
<option>15&deg; Antenna Polarization Mismatch&nbsp;&nbsp;(0.3 dB)</option>
<option>Linear-to-Circular Antenna Polarization Mismatch&nbsp;&nbsp;(3 dB)</option>
<option>Knife-Edge Diffraction</option>
<option>Ground reflections</option>
<option>Buildings, Billboards, Large Industrial Structures, etc.</option>
<option>Trees and Animals, etc.</option>
</select></td>
</tr>
<tr><td></td></tr>
</table>
</td>
</tr>
</table>

<br><br>

<table border="4" cellpadding="8">
<tr>
<td colspan="10" bgcolor="#7EBDE5"><font size="5"><b>Receiver Site Information</b></font></td>
</tr>
</table>

<table border="1" width="100%">
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="0" width="75%">
<tr><td></td></tr>
<tr>
<td align="right"><b>Site Name&nbsp;&nbsp;</b></td> 
<td><input type="text" name="rx_name" size="15" value="RX"></td> 
<td></td>
</tr>

<tr>
<td align="right"><b>Equipment Model / Notes</b></td>
<td><input type="text" name="rx_notes" size="30 value="">
</tr>

<tr>
<td align="right"><b>Site Latitude</b></td>
<td><input type="number" name="LAT2_D" min="0" max="90" value="44" step="1">&nbsp;&deg;&nbsp;
<input type="number" name="LAT2_M" min="0" max="59" value="30" step="1">&nbsp;'&nbsp;
<input type="number" name="LAT2_S" min="0" max="59.99" value="4.0" step="0.01">&nbsp;"</td>
<td><input type="radio" name="LAT2_val" value="North" checked>North&nbsp;&nbsp;
<input type="radio" name="LAT2_val" value="South">&nbsp;South&nbsp;&nbsp;(WGS84)</td>
</tr>

<tr>
<td align="right"><b>Site Longitude</b></td>
<td><input type="number" name="LON2_D" min="0" max="180" value="87" step="1">&nbsp;&deg;&nbsp;
<input type="number" name="LON2_M" min="0" max="59" value="56" step="1">&nbsp;'&nbsp;
<input type="number" name="LON2_S" min="0" max="59.99" value="51.00" step="0.01">&nbsp;"</td>
<td><input type="radio" name="LON2_val" value="West" checked>West&nbsp;&nbsp;
<input type="radio" name="LON2_val" value="East">&nbsp;East</td>
</tr>

<tr>
<td align="right"><b>Receiver Transmission Line Type</b></td>
<td><select name="rx_cab">
<option selected>Times Microwave LMR-400</option>
<option>Times Microwave LMR-400 UltraFlex</option>
<option>Times Microwave LMR-500</option>
<option>Times Microwave LMR-600</option>
<option>Times Microwave LMR-900</option>
<option>Times Microwave LMR-1200</option>
<option>Times Microwave LMR-1700</option>
<option>Andrew HELIAX LDF4-50A</option>
<option>Andrew HELIAX LDF5-50A</option>
<option>Andrew HELIAX LDF6-50</option>
<option>Andrew HELIAX LDF7-50A</option>
<option>Belden 9913 (RG-8)</option>
<option>Belden 8267 (RG-213)</option>
<option>Belden 9258 (RG-8X)</option>
<option>Belden 8240 (RG-58)</option>
<option>Crap RG-8</option>
<option>Other</option>
</select>
</td><td></td>
</tr>

<tr>
<td bgcolor="#BABBBE" align="right"><b>If </b><font color="maroon">Other</font><b>, Enter Transmission Line Loss Specification</b></td>
<td bgcolor="#BABBBE"><input type="number" name="rx_cab_other" min="0.00" max="99.90" value="0.00" step="0.01"> dB</td>
<td bgcolor="#BABBBE">
<input type="radio" name="check2" value="feet" checked>&nbsp;per 100 feet&nbsp;&nbsp;
<input type="radio" name="check2" value="meters">&nbsp;per 100 meters
</td>
</tr>

<tr>
<td align="right"><b>External Transmission Line Length</b></td>
<td><input type="number" name="rx_len" min="1.0" max="999.9" value="28.0" step="0.1">
<select name="rx_len_val">
<option selected>feet</option>
<option>meters</option>
</select>
<td></td>
</tr>

<tr>
<td align="right"><b>Antenna Height (Center-of-Radiation)</b></td>
<td><input type="number" name="rx_ant_ht" min="1.0" max="2000.0" value="15.0" step="0.1">
<select name="rx_ant_ht_val">
<option selected>feet</option>
<option>meters</option></select>
<td>Above Ground Level</td>
</tr>

<tr>
<td align="right"><b>Antenna Peak Gain</b></td>
<td><input type="number" name="rx_ant_gain" min="0.0" max="60.0" value="22.0" step="0.1">
<select name="rx_ant_val">
<option selected>dBi</option>
<option>dBd</option>
</select>
&nbsp;&nbsp;Radome Loss <input type="number" name="rx_ant_gain_radome" min="0.00" max="3.00" value="0.00" step="0.01"> dB
<td>(Note 1)</td>
</tr>

<tr>
<td align="right"><b>Antenna Model / Notes</b></td>
<td><input type="text" name="rx_ant_notes" size="30" value="">
<td></td>
</tr>

<tr>
<td align="right"><b>Miscellaneous Transmission Line Losses</b></td>
<td><input type="number" name="rx_misc_cab_loss" min="0.00" max="99.90" value="0.00" step="0.01"> dB</td>
<td>
<select name="null">
<option selected> -- EXAMPLES --</option>
<option>2-port splitter, 3.5 dB loss</option>
<option>4-port splitter, 6.5 dB loss</option>
<option>PolyPhaser, 0.2 dB loss</option>
<option>Right-angle N adapter, 0.5 dB loss</option>
<option>RF connector, 0.15 dB loss</option>
<option>DC injector, 0.2 dB loss</option>
<option>Isolator, 0.8 dB loss</option>
<option>Filter, 2 dB loss</option>
<option>RF branching loss</option>
<option>Flex jumpers</option>
<option>Standby switches</option>
</select></td>
</tr>

<tr>
<td align="right"><b>Miscellaneous Gains, Before Line/Misc. Loss</b></td>
<td><input type="number" name="rx_misc_gain" min="0.0" max="60.0" value="0.0" step="0.1"> dB</td>
<td>
<select name="null">
<option selected>-- EXAMPLES --</option>
<option>Tower top receive preamplifier, 17 dB gain</option>
</select></td>
</tr>

<tr>
<td align="right"><b>Receiver Threshold</b></td>
<td><input type="number" name="BER" min="-140.0" max="10.0" value="-90.0" step="0.1"> dBm
&nbsp;&nbsp;Criteria <select name="BER_crit">
<option>10-3 BER</option>
<option>10-6 BER</option>
<option>RBER</option>
<option>SES BER</option>
<option>12 dB SINAD</option>
</select></td>
<td>Sensitivity</td>
</tr>

<tr><td></td></tr>

<tr>
<td bgcolor="#CCBBBB" align="right">Following <font color="maroon">TWO</font> questions are for Vertical Space Diversity systems <i>ONLY</i></td>
<td bgcolor="#CCBBBB">&nbsp;&nbsp;&#8628;</td>
<td bgcolor="#CCBBBB">(Note 1 &amp; 2)</td>
</tr>

<tr>
<td bgcolor="#CCBBBB" align="right"><b>Diversity Antenna Spacing (Center-of-Radiation)</b></td>
<td bgcolor="#CCBBBB"><input type="number" name="rx_div_ant_ht" min="0.00" max="999.99" value="0.00" step="0.01">
<select name="rx_div_ant_ht_val">
<option selected>feet</option>
<option>meters</option>
</select>
<td bgcolor="#CCBBBB"></td>
</tr>

<tr>
<td bgcolor="#CCBBBB" align="right"><b>Diversity Antenna Peak Gain</b></td>
<td bgcolor="#CCBBBB"><input type="number" name="rx_div_ant_gain" min="1.0" max="60.0" value="22.0" step="0.1">
<select name="rx_div_ant_val">
<option selected>dBi</option>
<option>dBd</option>
</select>
&nbsp;&nbsp;Radome Loss <input type="number" name="rx_div_ant_gain_radome" min="0.00" max="3.00" value="0.00" step="0.01"> dB
<td bgcolor="#CCBBBB"></td>
</tr>

<tr><td></td></tr>

<tr>
<td bgcolor="#CCCCBB" align="right">Following <font color="maroon">THREE</font> questions are for Digital Data systems <i>ONLY</i></td>
<td bgcolor="#CCCCBB">&nbsp;&nbsp;&#8628;</td>
<td bgcolor="#CCCCBB"></td>
</tr>

<tr>
<td bgcolor="#CCCCBB" align="right"><b>Receiver Dispersive Fade Margin (DFM)</b></td>
<td bgcolor="#CCCCBB"><input type="number" name="dfm" min="0.0" max="99.9" value="0.0" step="0.1"> dB</td>
<td bgcolor="#CCCCBB">(Note 3)</td>
</tr>

<tr>
<td bgcolor="#CCCCBB" align="right"><b>Receiver External Interference Fade Margin (EIFM)</b></td>
<td bgcolor="#CCCCBB"><input type="number" name="eifm" min="0.0" max="99.9" value="0.0" step="0.1"> dB</td>
<td bgcolor="#CCCCBB">(Note 4)</td>
</tr>

<tr>
<td bgcolor="#CCCCBB" align="right"><b>Receiver Adjacent Channel Interference Fade Margin (AIFM)</b></td>
<td bgcolor="#CCCCBB"><input type="number" name="aifm" min="0.0" max="99.9" value="0.0" step="0.1"> dB</td>
<td bgcolor="#CCCCBB">(Note 5)</td>
</tr>
<tr><td></td></tr>
</table>
</td>
</tr>
</table>

<br><br>

<table border="4" cellpadding="8">
<tr>
<td colspan="10" bgcolor="#7EBDE5"><font size="5"><b>Environmental Information</b></font></td>
</tr>
</table>

<table border="1" width="100%">
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="0" width="75%">
<tr><td></td></tr>
<tr>
<td align="right"><b>Would You Like to Calculate the Effective Earth Radius, K-Factor?</b></td>
<td><input type="radio" name="check3" value="yes">Yes&nbsp;&nbsp;<input type="radio" name="check3" value="no" checked>No</td>
<td></td>
</tr>

<tr>
<td bgcolor="#BABBBE" align="right"><b>If </b><font color="maroon">No</font><b>, Select the Effective Earth Radius, K-Factor</b></td>
<td bgcolor="#BABBBE"><select name="k">
<option>5/12</option>
<option>1/2</option>
<option>2/3</option>
<option>1.0</option>
<option>7/6</option>
<option>5/4</option>
<option selected>4/3</option>
<option>5/3</option>
<option>7/4</option>
<option>2.0</option>
<option>3.0</option>
<option>4.0</option>
<option>20.0</option>
<option>Infinity</option>
</select></td>
<td bgcolor="#BABBBE">(Note 6)</td>
</tr>

<tr>
<td bgcolor="#BBCCBB"align="right">If <font color="maroon">Yes</font>, answer the following <font color="maroon">THREE</font> questions</td>
<td bgcolor="#BBCCBB">&nbsp;&nbsp;&#8628;</td>
<td bgcolor="#BBCCBB"></td>
</tr>

<tr>
<td bgcolor="#BBCCBB" align="right"><b>General Site Elevation</b></td>
<td bgcolor="#BBCCBB"><input type="number" name="k_ht" min="0" max="9999" value="0" step="1">
<select name="k_ht_val">
<option selected>feet</option>
<option>meters</option></select>
<td bgcolor="#BBCCBB">Above Mean Sea Level</td>
</tr>

<tr>
<td bgcolor="#BBCCBB" align="right"><b>Average Annual Relative Humidity</b></td>
<td bgcolor="#BBCCBB"><input type="number" name="rh" min="1" max="99" value="76" step="1"> percent</td>
<td bgcolor="#BBCCBB">(Note 7)</td>
</tr>

<tr>
<td bgcolor="#BBCCBB" align="right"><b>Average Annual Barometric Pressure</b></td>
<td bgcolor="#BBCCBB"><input type="number" name="baro" min="1.0" max="99.0" value="30.0" step="0.1"> inches of mercury</td>
<td bgcolor="#BBCCBB">(Note 8)</td>
</tr>

<tr><td></td></tr>

<tr>
<td align="right"><b>Would You Like to Calculate the Vigants-Barnett Climate Factor?</b></td>
<td><input type="radio" name="check4" value="yes">Yes&nbsp;&nbsp;
<input type="radio" name="check4" value="no" checked>No</td>
<td>(Note 9)</td>
</tr>

<tr>
<td bgcolor="#BABBBE" align="right"><b>If </b><font color="maroon">No</font><b>, Choose the Vigants-Barnett (Outage) Climate Factor</b></td>
<td bgcolor="#BABBBE"><select name="vigants">
<option>0.25 : Mountainous, very rough, very dry but non-reflective</option>
<option>0.50 : Dry desert climate</option>
<option selected>1.00 : Average terrain, with some roughness</option>
<option>2.00 : Great Lakes area</option>
<option>4.00 : Very smooth terrain, over water or flat desert, non-coastal</option>
<option>6.00 : Very smooth terrain, over water or flat desert, coastal</option>
</select></td>
<td bgcolor="#BABBBE"></td>
</tr>

<tr>
<td bgcolor="#A3A3A3" align="right">If <font color="maroon">Yes</font>, answer the following <font color="maroon">TWO</font> questions</td>
<td bgcolor="#A3A3A3">&nbsp;&nbsp;&#8628;</td>
<td bgcolor="#A3A3A3"></td>
</tr>

<tr>
<td bgcolor="#A3A3A3" align="right"><b>Average Terrain Roughness</b></td>
<td bgcolor="#A3A3A3"><input type="number" name="rough" min="0" max="140" value="0" step="1">
<select name="rough_val">
<option selected>feet</option>
<option>meters</option>
</select> Std. Deviation of Elevations</td>
<td bgcolor="#A3A3A3">(Note 10)</td>
</tr>

<tr>
<td bgcolor="#A3A3A3" align="right"><b>Local Area Humidity Type</b></td>
<td bgcolor="#A3A3A3"><select name="rough_hum">
<option>Coastal, Very Humid Areas</option>
<option>Non-Coastal, Humid Areas</option>
<option selected>Average or Temperate Areas</option>
<option>Dry Areas</option>
</select></td>
<td bgcolor="#A3A3A3"></td>
</tr>

<tr><td></td></tr>

<tr>
<td align="right"><b><a href="../pics/Annual_Average_Temperature_Map.png">Average Annual Temperature</a></b></td>
<td><input type="number" name="temp" min="1.0" max="99.0" value="50.0" step="0.1">
<select name="temp_val">
<option>celsius</option>
<option selected>fahrenheit</option>
</select></td>
<td></td>
</tr>

<tr>
<td align="right"><b>Select the Crane Rain Region</b></td>
<td><select name="rain">
<option>A: Polar Tundra</option>
<option>B: Polar Taiga - Moderate</option>
<option>C: Temperate Maritime</option>
<option selected>D1: Temperate Continental - Dry</option>
<option>D2: Temperate Continental - Mid</option>
<option>D3: Temperate Continental - Wet</option>
<option>E: Subtropical - Wet</option>
<option>F: Subtropical - Arid</option>
<option>G: Tropical - Moderate</option>
<option>H: Tropical - Wet</option>
<option>None</option>
</select></td>
<td><a href="http://www.gbppr.net/splat/path.html">Rain Regions</a></td>
</tr>

<tr>
<td bgcolor="#BABBBE" align="right"><b>If</b> <font color="maroon">None</font><b>, Enter a (0.01%) Precipitation Rate</b></td>
<td bgcolor="#BABBBE"><input type="number" name="rate" min="1.0" max="199.9" value="37.0" step="0.1"> mm/hour</td>
<td bgcolor="#BABBBE">(Note 11)</td>
</tr>

<tr>
<td align="right"><b>Water Vapor Density</b></td>
<td><input type="number" name="wvd" min="1.0" max="99.0" value="7.5" step="0.1"> grams/m<sup>3</sup></td>
<td>Moderate Humidity</td>
</tr>

<tr>
<td align="right"><b>Percent Fresnel Zone to Calculate</b></td>
<td><input type="number" name="nth" min="10" max="400" value="60" step="10"> %
<td>(Note 12)</td>
</tr>

<tr>
<td align="right"><b>Select Your State for City and County Plotting</b></td>
<td><select name="geo">
<option>NONE</option>
<option>AK</option>
<option>AL</option>
<option>AZ</option>
<option>AR</option>
<option>CA</option>
<option>CO</option>
<option>CT</option>
<option>DE</option>
<option>FL</option>
<option>GA</option>
<option>HI</option>
<option>ID</option>
<option>IL</option>
<option>IN</option>
<option>IA</option>
<option>KS</option>
<option>KY</option>
<option>LA</option>
<option>ME</option>
<option>MD</option>
<option>MA</option>
<option>MI</option>
<option>MN</option>
<option>MS</option>
<option>MO</option>
<option>MT</option>
<option>NE</option>
<option>NV</option>
<option>NH</option>
<option>NJ</option>
<option>NM</option>
<option>NY</option>
<option>NC</option>
<option>ND</option>
<option>OH</option>
<option>OK</option>
<option>OR</option>
<option>PA</option>
<option>RI</option>
<option>SC</option>
<option>SD</option>
<option>TN</option>
<option>TX</option>
<option>UT</option>
<option>VT</option>
<option>VA</option>
<option>WA</option>
<option>WV</option>
<option selected>WI</option>
<option>WY</option>
<option>NONE</option>
</select>
<td>(Note 13)</td>
</tr>

<tr>
<td align="right"><b>Additional Ground Clutter</b></td>
<td><input type="number" name="gc" min="0" max="100" value="0" step="1">
<select name="gc_val">
<option selected>feet</option>
<option>meters</option></select></td>
<td>(Note 14)
<tr><td></td></tr>
</tr>
</table>
</td>
</tr>
</table>

<br><br>
<table border="4" cellpadding="8">
<tr>
<td colspan="10" bgcolor="#7EBDE5"><font size="5"><b>Longley-Rice Path Calculation Parameters</b></font></td>
</tr>
</table>

<table border="1" width="100%">
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="0" width="75%">
<tr><td></td></tr>
<tr>
<td align="right"><b><a href="http://ham-radio.com/k6sti/hfgc.htm">Ground Dielectric Constant</a></b></td>
<td><input type="number" name="diecon" min="1" max="99" value="15"> Soil Permittivity</td>
<td>(Note 15)</td>
</tr>

<tr>
<td align="right"><b><a href="https://www.fcc.gov/sites/default/files/am_m3_usa_medium.png">Ground Conductivity</a></b></td>
<td><input type="number" name="earcon" min="1" max="30" value="8">
<a href="https://www.epa.gov/environmental-geophysics/electrical-conductivity-and-resistivity">milliSiemens per meter</a></td>
<td>(Note 16)</td>
</tr>

<tr>
<td align="right"><b>Select the <a href="https://en.wikipedia.org/wiki/Longley%E2%80%93Rice_model">Longley-Rice</a> Climate Type</b></td>
<td><select name="climate">
<option>Equatorial</option>
<option>Continental Subtropical</option>
<option>Maritime Subtropical</option>
<option>Desert</option>
<option selected>Continental Temperate</option>
<option>Maritime Temperate, Overland</option>
<option>Maritime Temperate, Oversea</option>
</select></td>
<td>(Note 17)</td>
</tr>

<tr>
<td align="right"><b>Antenna Polarization</b></td>
<td><select name="polar">
<option>Horizontal</option>
<option selected>Vertical</option>
</select></td>
<td>(Note 18)</td>
</tr>

<tr>
<td align="right"><b>Situation Variability (Confidence)</b></td>
<td><input type="number" name="sit" min="3" max="99" value="50"> %</td>
<td>(Note 19)</td>
</tr>

<tr>
<td align="right"><b>Time Variability (Reliability)</b></td>
<td><input type="number" name="time" min="3" max="99" value="90"> %</td>
<td>(Note 20)</td>
</tr>
<tr><td></td></tr>
</table>
</td>
</tr>
</table>

<br><br>
<table border="4" cellpadding="8">
<tr>
<td colspan="10" bgcolor="#7EBDE5" align="center"><font size="5"><b>Image Quality &amp; Terrain Resolution</b></font></td>
</tr>
</table>

<table border="1" width="100%">
<tr>
<td>
<table border="0" cellpadding="4" cellspacing="0" width="75%">
<tr><td></td></tr>
<tr>
<td align="right"><b>Select Terrain Resolution Quality</b></td>
<td><select name="quality">
<option selected>Low / Fast</option>
<option>High / Slow</option>
</select></td>
<td>(Note 21)</td>
</tr>
<tr><td></td></tr>
</table>
</td>
</tr>
</table>

</blockquote>

<br>

<center>
<table border="2" cellpadding="10">
<p>Press <b>Submit</b> to see an example.<br><font color="red">Only Press <b>Submit</b> Once!</font><br>It will take awhile for the plotting to complete.</p>
<tr>
<td bgcolor="#3240A8"><input type="submit" value="Submit"></td>
<td bgcolor="#3240A8"><input type="reset" value="Clear"></td>
</tr>
</table>
</center>
</form>

<blockquote>
<p><b><u>Notes</u></b></p>

<blockquote>
<p><a href="http://www.gbppr.net/splat/path.html">Microwave Radio Path Analysis Notes</a>&nbsp;&nbsp;Read this first.</p>

<p>1.)&nbsp;&nbsp;Don't forget to take into account any radome loss.&nbsp;&nbsp;For sealed Yagi antennas, radome loss is usually included in the antenna's specified gain.&nbsp;&nbsp;"Wet" radome loss can be 2 dB or more.</p>

<p>2.)&nbsp;&nbsp;Arvids Vigants' space diversity improvement equation is <i>only accurate</i> for paths with the following parameters: Distance: 14-40 miles, Frequency: 2-11 GHz, Spacing: 10-50 feet, Div. Gain: 0-6 dB of Primary, Fade Margin: 30-50 dB.&nbsp;&nbsp;The diversity antenna cable type is assumed the same as the main receiver's.&nbsp;&nbsp;Space diversity is usually required when crossing flat, wet surfaces or in very humid climates.</p>

<p>3.)&nbsp;&nbsp;Dispersive fade margin is provided by your radio's manufacturer, and is determined by the type of modulation, effectiveness of any equalization in the receive path, and the multipath signal's time delay.&nbsp;&nbsp;Dispersive fade margin characterizes the radio's robustness to dispersive (spectrum-distoring) fades.</p>

<p>4.)&nbsp;&nbsp;External interference fade margin is receiver threshold degradation due to interference from external systems.</p>

<p>5.)&nbsp;&nbsp;Adjacent channel interference fade margin accounts for receiver threshold degradation due to interference from adjacent channel transmitters in one's own system.&nbsp;&nbsp;This is usually a negligible parameter except in frequency diversity and N+1 multiline systems.</p>

<p>6.)&nbsp;&nbsp;<a href="https://en.wikipedia.org/wiki/Line-of-sight_propagation#Atmospheric_refraction">K-Factor</a> of 1.0 is the true Earth radius and "Infinity" is a flat Earth.&nbsp;&nbsp;Radio waves tend to "travel farther" than optical waves due to atmospheric refraction.&nbsp;&nbsp;A K-Factor less than 1.0 means the RF path bends <i>upwards</i> (sub-refractive) into the atmosphere, while a K-Factor greater than 1.0 mean it bends downward (super-refractive).&nbsp;&nbsp;A K-Factor of 4/3 (1.33) is often used as a compromise.</p>

<blockquote>
<table border="1" cellpadding="3">
<tr>
<td bgcolor="#CFCFCF">
<pre>
<b>K-Factor         Propagation    Weather                      Terrain</b>
4/3              Perfect        Standard Atmosphere          Temperate Zone, No Fog
1.0 to 4/3       Ideal          No Surface Layers, Fog       Dry, Mountainous, No Fog
2/3 to 1.0       Average        Substandard, Light Fog       Flat, Temperate, Some Fog
1/2 to 2/3       Difficult      Surface Layers, Ground Fog   Coastal
5/12 to 1/2      Bad            Fog Moisture, Over Water     Coastal, Water, Tropical
</pre>
</td>
</tr>
</table>
</blockquote>

<p>7.)&nbsp;&nbsp;<a href="https://sage.nelson.wisc.edu/data-and-models/atlas-of-the-biosphere/mapping-the-biosphere/ecosystems/average-annual-relative-humidity/">Average Annual Relative Humidity</a></p>

<p>8.)&nbsp;&nbsp;</p>

<p>9.)&nbsp;&nbsp;The Climate Factor, or C-Factor, is a parameter in the Vigants-Barnett model used to predict outage probability.&nbsp;&nbsp;The Vigants-Barnett reliability method allows users to automatically calculate the C-Factor and terrain roughness.</p>

<p>10.)&nbsp;&nbsp;Example standard deviation of the terrain elevations: 29 feet - for smooth and over-water terrain, 50 feet - for average terrain with some roughness, 120 feet - for mountainous or very rough terrain.</p>

<p>11.)&nbsp;&nbsp;Choose a "worst case" scenario just to be safe.</p>

<p>12.)&nbsp;&nbsp;The first <a href="https://en.wikipedia.org/wiki/Fresnel_zone">Fresnel zone</a> corresponds to the main lobe, which contains the vast majority of the RF energy.&nbsp;&nbsp;60% of this zone must be <i>free of physical obstructions</i> for the microwave path to be successful.&nbsp;&nbsp;For highest link reliability, at least 30% of the first <a href="https://en.wikipedia.org/wiki/Fresnel_zone">Fresnel zone</a> at K = 2/3 or 100% of the first <a href="https://en.wikipedia.org/wiki/Fresnel_zone">Fresnel zone</a> at K = 4/3 should also be clear.</p>

<p>13.)&nbsp;&nbsp;Attempts to determine you country, state, and city based on the transmitter site LAT/LON by using OpenStreetMaps.</p>

<p>14.)&nbsp;&nbsp;Ground clutter has the effect of raising the overall terrain by the specified amount, except over areas at sea-level and at the transmitting and receiving antenna locations.&nbsp;&nbsp;The input is a generic range from 0 to 100.&nbsp;&nbsp;Select "feet" for 0 to 100 feet (1 foot increments) or select "meters" to increase the range from 0 to 330 feet (3.3 foot increments).</p>

<p>15.)&nbsp;&nbsp;</p>

<p>16.)&nbsp;&nbsp;<a href="https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.832-2-199907-S!!PDF-E.pdf">Worldwide Map of Ground Conductivity</a></p>

<p>17.)&nbsp;&nbsp;</p>

<p>18.)&nbsp;&nbsp;Horizontal polarization will generally provide less multipath in urban areas and may provide lower path loss in non line-of-sight situations.&nbsp;&nbsp;It is also better in reducing foliage attenuation.&nbsp;&nbsp;Over water, or other flat reflective surfaces, vertical polarization will offer less path loss. </p>

<p>19.)&nbsp;&nbsp;Here is a good overview of Longley-Rice <a href="https://www.softwright.com/faq/support/longley_rice_variability.html">Situation Variability</a>.&nbsp;&nbsp;Reception is usually described as LR(50/90).&nbsp;&nbsp;This is a 50% confidence that reception at a certain signal level will be received 90% of the time.</p>

<p>20.)&nbsp;&nbsp;Here is a good overview of Longley-Rice <a href="https://www.softwright.com/faq/support/longley_rice_variability.html">Time Variability</a>.</p>

<p>21.)&nbsp;&nbsp;Uses <a href="https://en.wikipedia.org/wiki/Shuttle_Radar_Topography_Mission">Shuttle Radar Topography Mission</a> elevation data for terrain generation.&nbsp;&nbsp;<b>Low / Fast</b> uses 3 arc-second resolution, and <b>High / Slow</b> uses 1 arc-second resolution.&nbsp;&nbsp;Only a few LAT/LONS (mostly in the U.S.) work with HD resolution terrain data right now, and the plotting is quite slow.</p>
</blockquote>

<p>Plotting done using <a href="http://www.gbppr.net/splat">SPLAT! v2.0</a> by <a href="http://www.qsl.net/kd2bd">John A. Magliacane</a> (KD2BD) and <a href="https://github.com/hoche/splat">hoche</a>.</p>

<p>The Elevation Profile displays the elevation and depression angles resulting from the terrain between the receiver's location and the transmitter site from the perspective of the receiver's location.&nbsp;&nbsp;A second trace is plotted between the left-side of the graph (receiver's location) and the location of the transmitting antenna on the right.&nbsp;&nbsp;This trace illustrates the elevation angle required for a line-of-sight path to exist between the receiver and transmitter locations.&nbsp;&nbsp;If the trace intersects the elevation profile at any point on the graph, then this is an indication that a line-of-sight path <i>does not</i> exist under the conditions given, and the obstructions can be clearly identified on the graph at the point(s) of intersection.</p>

<p>AGL- Above Ground Level.&nbsp;&nbsp;Height above common ground to the midpoint of the radiating antenna.&nbsp;&nbsp;AMSL - Above Mean Sea Level.&nbsp;&nbsp;Height referenced above sea level, or zero elevation.</p>

<p><b>Other Analysis Tools</b></p>

<ul>
<li><a href="linesite.main.cgi">Line-of-Sight Path Analysis</a></li>
<li><a href="longley.main.cgi">Longley-Rice Path Loss Analysis</a></li>
<li><a href="3dmap.main.cgi">3D Local Ground Elevation Map</a></li>
</ul>
</blockquote>

</font>
</body>
</html>
EOF
