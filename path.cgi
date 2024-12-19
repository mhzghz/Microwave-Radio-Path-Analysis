#!/usr/bin/perl

## --> Microwave Radio Path Analysis, path.cgi
## --> Green Bay Professional Packet Radio, www.gbppr.net

## This file Copyright 2003 <contact@gbppr.net> under the GPL.
## NO WARRANTY.  Please send bug reports / patches.

## Program Setup
#
$ENV{PATH} = "/bin:/usr/bin:/usr/local/bin";
select STDOUT;
$| = 1;
use Math::Trig;
use Math::Complex;
use Time::Piece; 
use Geo::Coder::OSM;       # For lat/lon to state decoding / Install: sudo cpan Geo::Coder::OSM
use Geo::Coordinates::UTM; # For UTM results / Install: sudo cpan Geo::Coordinates::UTM
use warnings;
require "flush.pl";

## User Setup
#
my $logo       = "../pics/gbppr.jpg";
my $banner     = "A service of Green Bay Professional Packet Radio - <a href=\"http://www.gbppr.net\">www.gbppr.net</a>";
my $url        = "http://gbppr.ddns.net/cgi-bin/path.main.cgi";
my $ver        = "v2.70"; # Dec2024
my $splat      = "/usr/local/bin/splat";
my $splatdir   = "/usr/splat/sdf";
my $splatdirhd = "/media/gbppr/500GB/sdf-hd";
my $gnuplot    = "/usr/bin/gnuplot";
my $htmldoc    = "/usr/bin/htmldoc";
my $do_mag     = "yes"; # Requires the installation of pygeomag: https://github.com/boxpet/pygeomag
my $do_utm     = "yes"; # Requires the installation of Geo::Coordinates::UTM
my $do_lulc    = "yes"; # Requires land usage data and the "ptelev" util from FCC's TVStudy program: https://www.fcc.gov/oet/tvstudy
my $DEBUG      = 0;  # 0=leave temp files 1=delete temp file

## Create a random directory for working files
#
my $sec = 0;
my $min = 0;
my $hour = 0;
my $mday = 0;
my $mon = 0;
my $year = 0;
($sec, $min, $hour, $mday, $mon, $year) = gmtime;
$mon  = sprintf "%02.0f", $mon + 1;
$mday = sprintf "%02.0f", $mday; 
$year = sprintf "%02.0f", $year;
$year = 1900 + $year;

my $RAN = sprintf "%.f", rand(10000000);
mkdir "tmp/$mon-$mday";
mkdir "tmp/$mon-$mday/$RAN";
chdir "tmp/$mon-$mday/$RAN";

## Print MIME
#
print "content-type:text/html\n\n";
&flush(STDOUT);

## Read Web Browser Environment
#
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
@pairs = split(/&/, $buffer);
foreach $pair (@pairs) {
  ($name, $value) = split(/=/, $pair);
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
  $FORM{$name} = $value;
}

my $frq = $FORM{'frq'};
my $frq_val = $FORM{'frq_val'};
my $frq_div = $FORM{'frq_div'};
my $frq_div_val = $FORM{'frq_div_val'};

my $pwr_out = $FORM{'pwr_out'};
my $pwr_out_val = $FORM{'pwr_out_val'};

my $project = $FORM{'project'};
my $tx_name = $FORM{'tx_name'};
my $tx_cab = $FORM{'tx_cab'};
my $tx_len = $FORM{'tx_len'};
my $tx_len_val = $FORM{'tx_len_val'};
my $tx_ant_gain = $FORM{'tx_ant_gain'};
my $tx_ant_gain_radome = $FORM{'tx_ant_gain_radome'};
my $tx_ant_val = $FORM{'tx_ant_val'};
my $tx_ant_ht = $FORM{'tx_ant_ht'};
my $tx_ant_ht_val = $FORM{'tx_ant_ht_val'};
my $tx_misc_loss = $FORM{'tx_misc_loss'};
my $tx_misc_cab_loss = $FORM{'tx_misc_cab_loss'};
my $tx_misc_gain = $FORM{'tx_misc_gain'};
my $tx_cab_other = $FORM{'tx_cab_other'};

my $LAT1_D = $FORM{'LAT1_D'};
my $LAT1_M = $FORM{'LAT1_M'};
my $LAT1_S = $FORM{'LAT1_S'};
my $LAT1_val = $FORM{'LAT1_val'};

my $LON1_D = $FORM{'LON1_D'};
my $LON1_M = $FORM{'LON1_M'};
my $LON1_S = $FORM{'LON1_S'};
my $LON1_val = $FORM{'LON1_val'};

my $LAT2_D = $FORM{'LAT2_D'};
my $LAT2_M = $FORM{'LAT2_M'};
my $LAT2_S = $FORM{'LAT2_S'};
my $LAT2_val = $FORM{'LAT2_val'};

my $LON2_D = $FORM{'LON2_D'};
my $LON2_M = $FORM{'LON2_M'};
my $LON2_S = $FORM{'LON2_S'};
my $LON2_val = $FORM{'LON2_val'};

my $rx_name = $FORM{'rx_name'};
my $rx_cab = $FORM{'rx_cab'};
my $rx_len = $FORM{'rx_len'};
my $rx_len_val = $FORM{'rx_len_val'};
my $rx_ant_gain = $FORM{'rx_ant_gain'};
my $rx_ant_gain_radome = $FORM{'rx_ant_gain_radome'};
my $rx_ant_val = $FORM{'rx_ant_val'};
my $rx_ant_ht = $FORM{'rx_ant_ht'};
my $rx_ant_ht_val = $FORM{'rx_ant_ht_val'};
my $rx_misc_cab_loss = $FORM{'rx_misc_cab_loss'};
my $rx_misc_gain = $FORM{'rx_misc_gain'};
my $rx_cab_other = $FORM{'rx_cab_other'};

my $rx_div_ant_ht = $FORM{'rx_div_ant_ht'};
my $rx_div_ant_ht_val = $FORM{'rx_div_ant_ht_val'};
my $rx_div_ant_gain = $FORM{'rx_div_ant_gain'};
my $rx_div_ant_gain_radome = $FORM{'rx_div_ant_gain_radome'};
my $rx_div_ant_val = $FORM{'rx_div_ant_val'};
my $rx_div_len = $FORM{'rx_div_len'};
my $rx_div_len_val = $FORM{'rx_div_len_val'};
my $rx_div_misc_cab_loss = $FORM{'rx_div_misc_cab_loss'};

my $BER = $FORM{'BER'};
my $BER_crit = $FORM{'BER_crit'};

my $dfm = $FORM{'dfm'};
my $eifm = $FORM{'eifm'};
my $aifm = $FORM{'aifm'};

my $nth = $FORM{'nth'};
my $k = $FORM{'k'};
my $vigants = $FORM{'vigants'};
my $temp = $FORM{'temp'};
my $temp_val = $FORM{'temp_val'};
my $rain = $FORM{'rain'};
my $geo = $FORM{'geo'};
my $rh = $FORM{'rh'};
my $baro = $FORM{'baro'};
my $rate = $FORM{'rate'};
my $envy = $FORM{'envy'};
my $wvd = $FORM{'wvd'};

my $check1 = $FORM{'check1'};
my $check2 = $FORM{'check2'};
my $check3 = $FORM{'check3'};
my $check4 = $FORM{'check4'};

my $rough = $FORM{'rough'};
my $rough_hum = $FORM{'rough_hum'};
my $rough_val = $FORM{'rough_val'};

my $gc = $FORM{'gc'};
my $gc_val = $FORM{'gc_val'};

my $k_ht = $FORM{'k_ht'};
my $k_ht_val = $FORM{'k_ht_val'};

my $earcon = $FORM{'earcon'};
my $diecon = $FORM{'diecon'};
my $climate = $FORM{'climate'};
my $polar = $FORM{'polar'};
my $sit = $FORM{'sit'};
my $time = $FORM{'time'};

my $quality = $FORM{'quality'};

my $tx_ant_notes = $FORM{'tx_ant_notes'};
my $rx_ant_notes = $FORM{'rx_ant_notes'};
my $tx_notes = $FORM{'tx_notes'};
my $rx_notes = $FORM{'rx_notes'};

## Subroutines
#
sub System {
  if ((0xffff & system $args) != 0 ) {
    print STDERR "error: $!\n";
    exit 1;
  }
}

## Coordinate Cleanup
#
$LAT1_D =~ tr/0-9.//csd;
$LAT1_M =~ tr/0-9.//csd;
$LAT1_S =~ tr/0-9.//csd;

$LON1_D =~ tr/0-9.//csd;
$LON1_M =~ tr/0-9.//csd;
$LON1_S =~ tr/0-9.//csd;

$LAT2_D =~ tr/0-9.//csd;
$LAT2_M =~ tr/0-9.//csd;
$LAT2_S =~ tr/0-9.//csd;

$LON2_D =~ tr/0-9.//csd;
$LON2_M =~ tr/0-9.//csd;
$LON2_S =~ tr/0-9.//csd;

if ($LAT1_D > 90 || $LAT1_D < 0) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT1_D &gt; 90 or $LAT1_D &lt; 0</b></font>\n";
  exit 1;
}
if ($LAT1_M >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT1_M &gt;= 60</b></font>\n";
  exit 1;
}
if ($LAT1_S >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT1_S &gt;= 60</b></font>\n"; 
  exit 1;
}

if ($LON1_D > 180) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON1_D &gt; 180</b></font>\n";
  exit 1;
}
if ($LON1_M >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON1_M &gt;= 60</b></font>\n"; 
  exit 1;
}
if ($LON1_S >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON1_S &gt;= 60</b></font>\n"; 
  exit 1;
}

if ($LAT2_D > 90 || $LAT2_D < 0) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT2_D &gt; 90 or $LAT2_D &lt; 0</b></font>\n";
  exit 1;
}
if ($LAT2_M >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT2_M &gt;= 60</b></font>\n";
  exit 1;
}
if ($LAT2_S >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LAT2_S &gt;= 60</b></font>\n";
  exit 1;
}

if ($LON2_D > 180) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON2_D &gt; 180</b></font>\n";
  exit 1;
}
if ($LON2_M >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON2_M &gt;= 60</b></font>\n";    
  exit 1;
}
if ($LON2_S >= 60) {
  print "<font color=\"red\"><b>BAD COORDINATES - $LON2_S &gt;= 60</b></font>\n"; 
  exit 1;
}

if ($LAT1_val eq "North") {
  $LAT1 = sprintf "%.6f", $LAT1_D + ($LAT1_M / 60) + ($LAT1_S / 3600);
  $LAT1_gnu = "N";
}
elsif ($LAT1_val eq "South") {
  $LAT1 = sprintf "-%.6f", $LAT1_D + ($LAT1_M / 60) + ($LAT1_S / 3600);
  $LAT1_gnu = "S";
}

if ($LON1_val eq "West") {
  $LON1 = sprintf "%.6f", $LON1_D + ($LON1_M / 60) + ($LON1_S / 3600);
  $LON1_geo = sprintf "-%.6f", $LON1_D + ($LON1_M / 60) + ($LON1_S / 3600);
  $LON1_gnu = "W";
}
elsif ($LON1_val eq "East") {
  $LON1 = sprintf "-%.6f", $LON1_D + ($LON1_M / 60) + ($LON1_S / 3600);
  $LON1_geo = sprintf "%.6f", $LON1_D + ($LON1_M / 60) + ($LON1_S / 3600);
  $LON1_gnu = "E";
}

if ($LAT2_val eq "North") {
  $LAT2 = sprintf "%.6f", $LAT2_D + ($LAT2_M / 60) + ($LAT2_S / 3600);
  $LAT2_gnu = "N";
}
elsif ($LAT2_val eq "South") {
  $LAT2 = sprintf "-%.6f", $LAT2_D + ($LAT2_M / 60) + ($LAT2_S / 3600);
  $LAT2_gnu = "S";
}

if ($LON2_val eq "West") {
  $LON2 = sprintf "%.6f", $LON2_D + ($LON2_M / 60) + ($LON2_S / 3600);
  $LON2_geo = sprintf "-%.6f", $LON2_D + ($LON2_M / 60) + ($LON2_S / 3600);
  $LON2_gnu = "W";
}
elsif ($LON2_val eq "East") {
  $LON2 = sprintf "-%.6f", $LON2_D + ($LON2_M / 60) + ($LON2_S / 3600);
  $LON2_geo = sprintf "%.6f", $LON2_D + ($LON2_M / 60) + ($LON2_S / 3600);
  $LON2_gnu = "E";
}

$LAT1_D = sprintf "%03d", $LAT1_D;
$LAT1_M = sprintf "%02d", $LAT1_M;
$LAT1_S = sprintf "%05.2f", $LAT1_S;

$LON1_D = sprintf "%03d", $LON1_D;
$LON1_M = sprintf "%02d", $LON1_M;
$LON1_S = sprintf "%05.2f", $LON1_S;

$LAT2_D = sprintf "%03d", $LAT2_D;
$LAT2_M = sprintf "%02d", $LAT2_M;
$LAT2_S = sprintf "%05.2f", $LAT2_S;

$LON2_D = sprintf "%03d", $LON2_D;
$LON2_M = sprintf "%02d", $LON2_M;
$LON2_S = sprintf "%05.2f", $LON2_S;

## Calculate Path Distance Based on LAT/LON
#
$H = ($LON1 - $LON2) * (68.962 + 0.04525 * (($LAT1 + $LAT2) / 2) - 0.01274 * (($LAT1 + $LAT2) / 2) ** 2 + 0.00004117 * (($LAT1 + $LAT2) / 2) ** 3);
$V = ($LAT1 - $LAT2) * (68.712 - 0.001184 * (($LAT1 + $LAT2) / 2) + 0.0002928 * (($LAT1 + $LAT2) / 2) ** 2 - 0.000002162 * (($LAT1 + $LAT2) / 2) ** 3);
$dist_mi = sqrt(($H ** 2) + ($V ** 2));
$dist_km = sprintf "%.2f", $dist_mi * 1.609344;
$dist_mi = sprintf "%.2f", $dist_mi;

if ($dist_mi > 200 || $dist_mi < 0 || !$dist_mi) {
  print "<font color=\"red\"><b>PATH LENGTH TOO LONG OR TOO SHORT (200 MILES MAX): $dist_mi</font>";
  exit 1;
}

## Get Primary/Diversity Frequency
#
$frq     =~ tr/0-9.//csd;
$frq_div =~ tr/0-9.//csd;

if ($frq < 0 || !$frq) {
  print "<font color=\"red\"><b>ENTER A FREQUENCY: $frq</b></font>";
  exit 1;
} 

if ($frq_val eq "GHz") {
  $frq_mhz = sprintf "%.4f", $frq * 1000; # convert GHz to MHz
  $frq_ghz = sprintf "%.4f", $frq;
} 
elsif ($frq_val eq "MHz") {
  $frq_ghz = sprintf "%.4f", $frq / 1000; # convert MHz to GHz
  $frq_mhz = sprintf "%.4f", $frq;
} 

if ($frq_mhz > 40000 || $frq_mhz < 20 || !$frq_mhz) {
  print "<font color=\"red\"><b>BAD PRIMARY FREQUENCY (20 - 40,000 MHz): $frq_mhz MHz</b></font>";
  exit 1;
}

if ($frq_ghz > 40 || $frq_ghz < 0.020 || !$frq_ghz) {
  print "<font color=\"red\"><b>BAD PRIMARY FREQUENCY (.020 - 40 GHz): $frq_ghz GHz</b></font>";
  exit 1;
}

if ($frq_div_val eq "GHz") {
  $frq_mhz_div = sprintf "%.4f", $frq_div * 1000; # convert GHz to MHz
  $frq_ghz_div = sprintf "%.4f", $frq_div;
}
elsif ($frq_div_val eq "MHz") {
  $frq_ghz_div = sprintf "%.4f", $frq_div / 1000; # convert MHz to GHz
  $frq_mhz_div = sprintf "%.4f", $frq_div;
}

if ($frq_mhz_div > 40000) {
  print "<font color=\"red\"><b>BAD DIVERSITY FREQUENCY (20 - 40,000 MHz): $frq_mhz_div MHz</b></font>";
}

if ($frq_ghz_div > 40) {
  print "<font color=\"red\"><b>BAD DIVERSITY FREQUENCY (.020 - 40 GHz): $frq_ghz_div GHz</b></font>";
}

## Calculate Wavelength
#
$wav_in = sprintf "%.3f", (299.792458 / $frq_mhz) * 39.370079; # wavelength in inches
$wav_ft = sprintf "%.3f", (299.792458 / $frq_mhz) * 3.2808399; # wavelength in feet
$wav_cm = sprintf "%.3f", (299.792458 / $frq_mhz) * 100;       # wavelength in centimeters
$wav_m  = sprintf "%.3f", (299.792458 / $frq_mhz);             # wavelength in meters
$wav_half_ft = ((299.792458 / $frq_mhz) * 3.2808399) / 2;      # 1/2 wavelength in feet

## Transmitter RF Output Power
#
$pwr_out =~ tr/0-9.-//csd;

if ($pwr_out_val eq "milliwatts") {
  $pwr_out = 10 * log10($pwr_out); # mW to dBm
}
elsif ($pwr_out_val eq "watts") {
  $pwr_out = 10 * log10($pwr_out) + 30; # Watts to dBm
  }
elsif ($pwr_out_val eq "kilowatts") {
  $pwr_out = 10 * log10($pwr_out) + 60; # kilowatts to dBm
}
elsif ($pwr_out_val eq "dBW") {
  $pwr_out = 10 * log10((10 ** (($pwr_out + 30) / 10))); # dBW to dBm
}
elsif ($pwr_out_val eq "dBk") {
  $pwr_out = 10 * log10((10 ** (($pwr_out + 60) / 10))); # dBk to dBm
}

# Do all path calculations in dBm
$pwr_out_mw  = sprintf "%.2f", 10 ** ($pwr_out / 10);
$pwr_out_w   = sprintf "%.2f", 10 ** (($pwr_out - 30) / 10);
$pwr_out_kw  = sprintf "%.2f", (10 ** (($pwr_out - 30) / 10)) / 1000;
$pwr_out_dbw = sprintf "%.2f", 10 * log10((10 ** (($pwr_out - 30) / 10)));
$pwr_out_dbk = sprintf "%.2f", (10 * log10((10 ** (($pwr_out - 30) / 10)))) - 30;
$pwr_out_dbm = sprintf "%.2f", $pwr_out;

## Get Fresnel zone
#
$nth =~ tr/0-9//csd;

if ($nth) {
  $fres = sprintf "%s", $nth; # For SPLAT! file
}


## Get Ground Clutter
#
$gc =~ tr/0-9//csd;

if ($gc_val eq "feet") {
  $gc_m  = sprintf "%.1f", $gc * 0.3048; # feet to meters
  $gc_ft = sprintf "%.1f", $gc;
}
elsif ($gc_val eq "meters") {
  $gc_ft = sprintf "%.1f", $gc / 0.3048; # meters to feet
  $gc_m  = sprintf "%.1f", $gc;
}

if ($gc_ft > 0) {
  $clutter = 1; # Do SPLAT! clutter
}
else {
  $clutter = 0; # Don't do SPLAT! clutter
}

## Transmitter Site Information
#
$OK_CHARS='-a-zA-Z0-9_.+=()\[\] ';# Allowed Characters

$project             =~ s/[^$OK_CHARS]//go;
$tx_ant_notes        =~ s/[^$OK_CHARS]//go;
$tx_notes            =~ s/[^$OK_CHARS]//go;
$tx_name             =~ tr/A-Za-z0-9//csd;
$tx_len              =~ tr/0-9.//csd;
$tx_ant_gain         =~ tr/0-9.//csd;
$rx_ant_gain_radome  =~ tr/0-9.//csd;
$tx_ant_ht           =~ tr/0-9.//csd;
$tx_misc_loss        =~ tr/0-9.//csd;
$tx_misc_cab_loss    =~ tr/0-9.//csd;
$tx_cab_other        =~ tr/0-9.//csd;
$tx_misc_gain        =~ tr/0-9.//csd;

# Limit characters for plotting
$project      = sprintf "%.26s", $project;
$tx_name      = sprintf "%.15s", $tx_name;
$tx_ant_notes = sprintf "%.20s", $tx_ant_notes;
$tx_notes     = sprintf "%.20s", $tx_notes;

if (!$tx_name) {
  $tx_name = "TX";
}
  
if ($tx_len < 1|| !$tx_len) {
  print "<font color=\"red\"><b>YOU NEED TO ENTER THE TRANSMITTER'S TOTAL CABLE LENGTH: $tx_len</b></font>";
  exit 1;
}

if ($tx_ant_ht < 1 || !$tx_ant_ht) {
  print "<font color=\"red\"><b>YOU NEED TO ENTER THE TRANSMITTER'S ANTENNA HEIGHT: $tx_ant_ht</b></font>";
  exit 1;
}

if ($tx_ant_ht_val eq "feet") {
  $tx_ant_ht_m  = sprintf "%.2f", $tx_ant_ht * 0.3048; # feet to meters
  $tx_ant_ht_ft = sprintf "%.2f", $tx_ant_ht;
}
elsif ($tx_ant_ht_val eq "meters") {
  $tx_ant_ht_ft = sprintf "%.2f", $tx_ant_ht / 0.3048; # meters to feet
  $tx_ant_ht_m  = sprintf "%.2f", $tx_ant_ht;
}

## Receiver Site Information
#
$rx_ant_notes           =~ s/[^$OK_CHARS]//go;
$rx_notes               =~ s/[^$OK_CHARS]//go;
$rx_name                =~ tr/A-Za-z0-9//csd;
$rx_len                 =~ tr/0-9.//csd;
$rx_ant_gain            =~ tr/0-9.//csd;
$rx_ant_gain_radome     =~ tr/0-9.//csd;
$rx_ant_ht              =~ tr/0-9.//csd;
$rx_misc_cab_loss       =~ tr/0-9.//csd;
$rx_cab_other           =~ tr/0-9.//csd;
$rx_misc_gain           =~ tr/0-9.//csd;
$rx_div_ant_ht          =~ tr/0-9.//csd;
$rx_div_ant_gain        =~ tr/0-9.//csd;
$rx_div_ant_gain_radome =~ tr/0-9.//csd;
$rx_div_len             =~ tr/0-9.//csd;
$rx_div_misc_cab_loss   =~ tr/0-9.//csd;

# Limit characters for plotting
$rx_name      = sprintf "%.15s", $rx_name;
$rx_ant_notes = sprintf "%.20s", $rx_ant_notes; 
$rx_notes     = sprintf "%.20s", $rx_ant_notes;

if (!$rx_name) {
  $rx_name = "RX";
}

if ($rx_len < 1 || !$rx_len) {
  print "<font color=\"red\"><b>YOU NEED TO ENTER THE RECEIVER'S TOTAL CABLE LENGTH: $rx_len</b></font>";
  exit 1;
}

if ($rx_ant_ht < 1 || !$rx_ant_ht) {
  print "<font color=\"red\"><b>YOU NEED TO ENTER THE RECEIVER'S ANTENNA HEIGHT: $rx_ant_ht</b></font>";
  exit 1;
}

if ($rx_ant_ht_val eq "feet") {
  $rx_ant_ht_m  = sprintf "%.2f", $rx_ant_ht * 0.3048; # feet to meters
  $rx_ant_ht_ft = sprintf "%.2f", $rx_ant_ht;
}
elsif ($rx_ant_ht_val eq "meters") {
  $rx_ant_ht_ft = sprintf "%.2f", $rx_ant_ht / 0.3048; # meters to feet
  $rx_ant_ht_m  = sprintf "%.2f", $rx_ant_ht;
}

## Get Antenna Gains (Minus Radome Loss)
#
if ($tx_ant_val eq "dBd") {
  $tx_ant_gain_dbi    = sprintf "%.2f", ($tx_ant_gain + 2.15) - $tx_ant_gain_radome; # dBd to dBi
  $tx_ant_gain_dbd    = sprintf "%.2f", $tx_ant_gain - $tx_ant_gain_radome;
  $tx_ant_gain_radome = sprintf "%.2f", $tx_ant_gain_radome;
}
elsif ($tx_ant_val eq "dBi") {
  $tx_ant_gain_dbd    = sprintf "%.2f", ($tx_ant_gain - 2.15) - $tx_ant_gain_radome; # dBi to dBd
  $tx_ant_gain_dbi    = sprintf "%.2f", $tx_ant_gain - $tx_ant_gain_radome;
  $tx_ant_gain_radome = sprintf "%.2f", $tx_ant_gain_radome;
}

if ($rx_ant_val eq "dBd") {
  $rx_ant_gain_dbi    = sprintf "%.2f", ($rx_ant_gain + 2.15) - $rx_ant_gain_radome; # dBd to dBi
  $rx_ant_gain_dbd    = sprintf "%.2f", $rx_ant_gain - $rx_ant_gain_radome;
  $rx_ant_gain_radome = sprintf "%.2f", $rx_ant_gain_radome;
}
elsif ($rx_ant_val eq "dBi") {
  $rx_ant_gain_dbd    = sprintf "%.2f", ($rx_ant_gain - 2.15) - $rx_ant_gain_radome; # dBi to dBd
  $rx_ant_gain_dbi    = sprintf "%.2f", $rx_ant_gain - $rx_ant_gain_radome;
  $rx_ant_gain_radome = sprintf "%.2f", $rx_ant_gain_radome;
}

## Get Diversity Antenna Parameters
#
if ($rx_div_ant_ht <= 1) {
  $do_div        = "no"; # Don't do diversity calculations if spacing is less than 10 feet
  $div_ft        = sprintf "%.2f", 0;
  $div_m         = sprintf "%.2f", 0;
  $div_ant_dbi   = sprintf "%.2f", 0;
  $div_ant_dbd   = sprintf "%.2f", 0;
  $div_ant_ht_ft = "Not Applicable";
  $div_ant_ht_m  = "N/A";
  $rx_div_ant_gain_radome = sprintf "%.2f", 0;
}
elsif ($rx_div_ant_ht > 1) {
  $do_div = "yes";

  if ($rx_div_ant_ht_val eq "feet") {
	$div_m  = $rx_div_ant_ht * 0.3048; # feet to meters
    $div_ft = $rx_div_ant_ht;
  }
  elsif ($rx_div_ant_ht_val eq "meters") {
    $div_ft = $rx_div_ant_ht / 0.3048; # meters to feet
    $div_m  = $rx_div_ant_ht;
  }

  if ($rx_div_ant_val eq "dBd") {
    $div_ant_dbi = sprintf "%.2f", ($rx_div_ant_gain + 2.15) - $rx_div_ant_gain_radome;
    $div_ant_dbd = sprintf "%.2f", $rx_div_ant_gain - $rx_div_ant_gain_radome;
  }
  elsif ($rx_div_ant_val eq "dBi") {
    $div_ant_dbd = sprintf "%.2f", ($rx_div_ant_gain - 2.15) - $rx_div_ant_gain_radome;
    $div_ant_dbi = sprintf "%.2f", $rx_div_ant_gain - $rx_div_ant_gain_radome;
  }

  $div_ant_ht_ft = sprintf "%.2f", ($div_ft + $rx_ant_ht_ft);
  $div_ant_ht_m  = sprintf "%.2f", ($div_ft + $rx_ant_ht_ft) * 0.3048;
  $div_ft        = sprintf "%.2f", $div_ft;
  $div_m         = sprintf "%.2f", $div_m;

  if ($div_ft > 50 || $div_ft < 9) {
    $div_ft_check = "(Spacing Error)";
  }
  else {
    $div_ft_check = "(Spacing O.K.)";
  }

  if (abs($rx_ant_gain_dbi - $div_ant_dbi) > 6) {
    $div_gain_check = "(Gain Error)";
  }
  else {
    $div_gain_check = "(Gain O.K.)";
  }
}

## Calculate vertical diversity spacing based on wavelength and distance
#
if ($do_div eq "yes") {

  # User supplied diversity spacing
  # Spacing should be an ODD multiple of 1/2 wavelength
  $div_check = sprintf "%.f", $div_ft / $wav_half_ft;

  if ($div_check % 2 == 0) {
    $div_check--;
  }
 
  # Adjust user supplied value
  $div_calc_ft = sprintf "%.2f", $div_check * $wav_half_ft;
  $div_calc_m  = sprintf "%.2f", $div_check * $wav_half_ft * 0.3048;

  # Calculate ideal spacing based on wavelength
  $div_space_m  = $wav_m * ((3 * ($dist_km * 1000)) / (8 * $tx_ant_ht_m));
  $div_space_ft = $div_space_m * 3.28084;

  if ($div_space_ft > 50) {
    $div_space_ft = 50;  # Vigants space diversity improvement equations are only accurate for 10-50 ft spacing
  }
 
  # Spacing should be an ODD multiple of 1/2 wavelength
  $div_check = sprintf "%.f", $div_space_ft / $wav_half_ft;

  if ($div_check % 2 == 0) {
    $div_check--;
  }
  
  # Adjust calculted value 
  $div_space_ft = sprintf "%.2f", $div_check * $wav_half_ft;
  $div_space_m  = sprintf "%.2f", $div_check * $wav_half_ft * 0.3048; # feet to meters

}
elsif ($do_div eq "no") {

  # Calculate ideal spacing based on wavelength
  $div_space_m  = $wav_m * ((3 * ($dist_km * 1000)) / (8 * $tx_ant_ht_m));
  $div_space_ft = $div_space_m * 3.28084;

  if ($div_space_ft > 50) {
    $div_space_ft = 50;  # Vigants space diversity improvement equations are only accurate for 10-50 ft spacing
  }

  # Spacing should be an ODD multiple of 1/2 wavelength
  $div_check = sprintf "%.f", $div_space_ft / $wav_half_ft;

  if ($div_check % 2 == 0) {
    $div_check--;
  }

  $div_space_ft = sprintf "%.2f", $div_check * $wav_half_ft;
  $div_space_m  = sprintf "%.2f", $div_check * $wav_half_ft * 0.3048; # feet to meters
  $div_calc_ft  = "Not Applicable";
  $div_calc_m   = "N/A";
}

## Average Annual Temperature
#
$temp =~ tr/0-9.//csd;

## F to Umm C & K
#
if ($temp_val eq "fahrenheit") {
  $temp_c = sprintf "%.1f", (5 / 9) * ($temp - 32);
  $temp_k = sprintf "%.1f", 273.15 + ((5 / 9) * ($temp - 32));
  $temp_f = sprintf "%.1f", $temp;
}
elsif ($temp_val eq "celsius") {
  $temp_f = sprintf "%.1f", ((9 / 5) * $temp) + 32;
  $temp_k = sprintf "%.1f", 273.15 + (((9 / 5) * $temp) + 32);
  $temp_c = sprintf "%.1f", $temp;
}

## Humidity & Pressure
#
$rh   =~ tr/0-9.//csd;
$baro =~ tr/0-9.//csd;

if (!$rh) {
  $rh = 50; # 50% relative humidity
}

if (!$baro) {
  $baro = 30; # 30 inches of mercury
}

## Get K-Factor
#
# check3 = Would You Like to Calculate the Effective Earth Radius, K-Factor?
if ($check3 eq "yes") {
  $k_ht =~ tr/0-9//csd; # Get general site elevation for k-factor

  if ($k_ht_val eq "meters") {
    $k_ht_m  = sprintf "%.2f", $k_ht;
    $k_ht_ft = sprintf "%.2f", $k_ht * 3.2808399;
  }
  if ($k_ht_val eq "feet") {
    $k_ht_m  = sprintf "%.2f", $k_ht * 0.3048;
    $k_ht_ft = sprintf "%.2f", $k_ht
  }
  
  # Atmospheric pressure from inches of mercury to millibars with sea level correction.
  $atmos_p = (33.86 * $baro) - ($k_ht_ft * 0.025);
  # Saturation vapor pressure, millibars
  $es = exp(1.805 + (0.0738 * $temp_c) - (0.000298 * ($temp_c ** 2)));
  # Partial vapor pressure, millibars
  $vapor_p = ($rh / 100) * $es;
  # Index of refraction
  $N = (77.6 / $temp_k) * ($atmos_p + (4810 * ($vapor_p / $temp_k)));
  # Effective Earth radius, K factor
  $k = sprintf "%.2f", 1 / (1 - 0.04665 * exp(0.005577 * $N));
  $k_str = sprintf "%.2f", $k;

  if (!$k) {
    $k = "1.33";
    $k_str = "4/3";
  }

  if ($N < 50) {
    $N = 50;
  }

  if ($N > 500) {
    $N = 500;
  }

  $nunits  = sprintf "%.f", $N;
  $vapor_p = sprintf "%.2f", $vapor_p;
  $es      = sprintf "%.2f", $es;
  $atmos_p = sprintf "%.2f", $atmos_p;
  $k_dec   = sprintf "%.2f", $k;
  $k_val   = "Calculated";
}
elsif ($check3 eq "no") {
  if ($k eq "5/12") {
    $k = 0.417;
    $k_str = "5/12";
  }
  elsif ($k eq "1/2") {
    $k = 0.500;
    $k_str = "1/2";
  }
  elsif ($k eq "2/3") {
    $k = 0.667;
    $k_str = "2/3";
  }
  elsif ($k eq "1.0") {
    $k = 1.001;  # to prevent divide-by-0 errors
    $k_str = "1.0";
  }
  elsif ($k eq "7/6") {
    $k = 1.167;
    $k_str = "7/6";
  }
  elsif ($k eq "5/4") {
    $k = 1.250;
    $k_str = "5/4";
  }
  elsif ($k eq "4/3") {
    $k = 1.333;
    $k_str = "4/3";
  }
  elsif ($k eq "5/3") {
    $k = 1.667;
    $k_str = "5/3";
  }
  elsif ($k eq "7/4") {
    $k = 1.750;
    $k_str = "7/4";
  }
  elsif ($k eq "2.0") {
    $k = 2.000;
    $k_str = "2.0";
  }
  elsif ($k eq "3.0") {
    $k = 3.000;
    $k_str = "3.0";
  }
  elsif ($k eq "4.0") {
    $k = 4.000;
    $k_str = "4.0";
  }
  elsif ($k eq "20.0") {
    $k = 20.000;
    $k_str = "20.0";
  }
  elsif ($k eq "Infinity") {
    $k = 100.000;
    $k_str = "Infinity";
  }
  
  ## Calculate N-units based on K-factor
  $nunits = 179.3 * (ln ((1 / 0.04665) * (1 - (1 / $k))));

  if ($nunits < 50) {
    $nunits = 50;
  }

  if ($nunits > 500) {
    $nunits = 500;
  }

  $nunits  = sprintf "%.f", $nunits;
  $vapor_p = "Not Applicable";
  $es      = sprintf "%.2f", exp(1.805 + (0.0738 * $temp_c) - (0.000298 * ($temp_c ** 2)));
  $atmos_p = sprintf "%.2f", 1013.25;
  $k_dec   = sprintf "%.2f", $k;
  $k_val   = "User Supplied";
}

## Get Earth Dielectric Constant
#
$diecon =~ tr/0-9//csd;

if ($diecon > 99  || $diecon < 0 || !$diecon) {
  $diecon = 15;
}

## Get Earth Conductivity
#
$earcon =~ tr/0-9//csd;

if ($earcon > 99 || $earcon < 0 || !$earcon) {
  $earcon = 5; # millisiemens per meter
}

$earcon = sprintf "%.3f", $earcon / 1000; # millisiemens to siemens

## Antenna Polarization
#
if ($polar eq "Vertical") {
  $ant = 1; # Vertical
}
elsif ($polar eq "Horizontal") {
  $ant = 0; # Horizontal
}

## Get Longley-Rice Confidence
#
$sit =~ tr/0-9//csd;
$si = sprintf "%.2f", $sit / 100;

## Get Longley-Rice Time
#
$time =~ tr/0-9//csd;
$ti = sprintf "%.2f", $time / 100;

## Get Longley-Rice Climate
#
if ($climate eq "Equatorial") {
  $cli = 1;
}
elsif ($climate eq "Continental Subtropical") {
  $cli = 2;
}
elsif ($climate eq "Maritime Subtropical") {
  $cli = 3;
}
elsif ($climate eq "Desert") {
  $cli = 4;
}
elsif ($climate eq "Continental Temperate") {
  $cli = 5;
}
elsif ($climate eq "Maritime Temperate, Overland") {
  $cli = 6;
}
elsif ($climate eq "Maritime Temperate, Oversea") {
  $cli = 7;
}

## Attempt to Get UTM Coordinates
#
if ($do_utm eq "yes") {
  # TX
  ($utm_zone_tx, $easting_tx, $northing_tx) = latlon_to_utm('WGS-84', $LAT1, $LON1_geo);
  # RX
  ($utm_zone_rx, $easting_rx, $northing_rx) = latlon_to_utm('WGS-84', $LAT2, $LON2_geo);

}
elsif ($do_utm eq "no") {
  $utm_zone_tx = "N/A";
  $easting_tx  = "N/A";
  $northing_tx = "N/A";
  $utm_zone_rx = "N/A";
  $easting_rx  = "N/A";
  $northing_rx = "N/A";
}

## Attempt to Get the State from the TX LAT/LON
#
my $geocoder = Geo::Coder::OSM->new();
my $result = $geocoder->reverse_geocode(lat => "$LAT1", lon => "$LON1_geo");
  
if ($result) {
  # Get state from OSM
  $country = $result->{address}{country};
  $state   = $result->{address}{state};
  $city    = $result->{address}{city};
  $county  = $result->{address}{county};
}
else {
  # Get user supplied state
  $geo =~ tr/A-Z//csd;
  $state = $geo;
}

if (!$county) { 
  $county = "N/A";
}
  
if (!$state) {
  $state = "N/A";
} 

if (!$city) {
  $city = $county;
}

## Convert State Names to 2-Letter Postal Codes
# 
if ($state eq "Alabama") {
  $state_name = "AL";
}
elsif ($state eq "Alaska") {
  $state_name = "AK";
}
elsif ($state eq "Arizona") {
  $state_name = "AR";
} 
elsif ($state eq "California") {
  $state_name = "CA";
}
elsif ($state eq "Colorado") { 
  $state_name = "CO";
}
elsif ($state eq "Connecticut") {
  $state_name = "CT";
}
elsif ($state eq "Delaware") {
  $state_name = "DE";
}
elsif ($state eq "District of Columbia") {
  $state_name = "DC";
}
elsif ($state eq "Florida") {
  $state_name = "FL";
}
elsif ($state eq "Georgia") {
  $state_name = "GA";
}
elsif ($state eq "Hawaii") { 
  $state_name = "HI";
}
elsif ($state eq "Idaho") {
  $state_name = "ID";
}
elsif ($state eq "Illinois") {
  $state_name = "IL";
}
elsif ($state eq "Indiana") {
  $state_name = "IN";
}
elsif ($state eq "Iowa") {
  $state_name = "IA";
}
elsif ($state eq "Kansas") {
  $state_name = "KS";
}
elsif ($state eq "Kentucky") {
  $state_name = "KY";
}
elsif ($state eq "Louisiana") {
  $state_name = "LA";
}
elsif ($state eq "Maine") {
  $state_name = "ME";
}
elsif ($state eq "Maryland") {
  $state_name = "MD";
}
elsif ($state eq "Massachusetts") {
  $state_name = "MA";
}
elsif ($state eq "Michigan") {
  $state_name = "MI";
}
elsif ($state eq "Minnesota") {
  $state_name = "MN";
}
elsif ($state eq "Mississippi") {
  $state_name = "MS";
}
elsif ($state eq "Missouri") {
  $state_name = "MO";
}
elsif ($state eq "Montana") {
  $state_name = "MT";
}
elsif ($state eq "Nebraska") {
  $state_name = "NE";
}
elsif ($state eq "Nevada") {
  $state_name = "NV";
}
elsif ($state eq "New Hampshire") {
  $state_name = "NH";
}
elsif ($state eq "New Mexico") {
  $state_name = "NM";
}
elsif ($state eq "New York") {
  $state_name = "NY";
}
elsif ($state eq "North Carolina") {
  $state_name = "NC";
}
elsif ($state eq "North Dakota") {
  $state_name = "ND";
}
elsif ($state eq "Ohio") {
  $state_name = "OH";
}
elsif ($state eq "Oklahoma") {
  $state_name = "OK";
}
elsif ($state eq "Oregon") {
  $state_name = "OR";
}
elsif ($state eq "Pennsylvania") {
  $state_name = "PA";
}
elsif ($state eq "Rhode Island") {
  $state_name = "RI";
}
elsif ($state eq "South Carolina") {
  $state_name = "SC";
}
elsif ($state eq "South Dakota") {
  $state_name = "SD";
}
elsif ($state eq "Tennessee") {
  $state_name = "TN";
}
elsif ($state eq "Texas") {
  $state_name = "TX";
}
elsif ($state eq "Utah") {
  $state_name = "UT";
}
elsif ($state eq "Vermont") {
  $state_name = "VT";
}
elsif ($state eq "Virginia") {
  $state_name = "VA";
}
elsif ($state eq "Washington") {
  $state_name = "WA";
}
elsif ($state eq "West Virginia") {
  $state_name = "WV";
}
elsif ($state eq "Wisconsin") {
  $state_name = "WI";
}
elsif ($state eq "Wyoming") {
  $state_name = "WY";
}
else {
  $state_name = "NONE";
}

if ($country eq "United States") {
  $cities   = $state_name . ".dat";
  $counties = $state_name . ".co.dat";
}

## Config SPLAT!
#
open(TX, ">", "tx.qth") or die "Can't open tx.qth: $!\n" ;
  print TX "$tx_name\n";
  print TX "$LAT1\n";
  print TX "$LON1\n";
  print TX "$tx_ant_ht_ft\n";
close TX;

open(RX, ">", "rx.qth") or die "Can't open rx.qth: $!\n";
  print RX "$rx_name\n";
  print RX "$LAT2\n";
  print RX "$LON2\n";
  print RX "$rx_ant_ht_ft\n";
close RX;

if ($do_div eq "yes") {
  $rx_div_name = $rx_name . "-DIV";
  open(RX, ">", "rx-div.qth") or die "Can't open rx-div.qth: $!\n";
    print RX "$rx_div_name\n";
    print RX "$LAT2\n";
    print RX "$LON2\n";
    print RX "$div_ant_ht_ft\n";
  close RX;
}

open(LR, ">", "tx.lrp") or die "Can't open tx.lrp: $!\n";
  print LR "$diecon\n";  # Earth Dielectric Constant (Relative permittivity) - 15.000
  print LR "$earcon\n";  # Earth Conductivity (Siemens per meter) - 0.005
  print LR "$nunits\n";  # Atmospheric Bending Constant (N-units) - 301.000
  print LR "$frq_mhz\n"; # # Frequency in MHz (20 MHz to 20 GHz)
  print LR "$cli\n";     # Radio Climate (5 = Continental Temperate)
  print LR "$ant\n";     # Polarization (0 = Horizontal, 1 = Vertical)
  print LR "$si\n";      # Fraction of situations (50% of locations)
  print LR "$ti\n";      # Fraction of time (90% of the time)
  print LR "0\n";        # Effective Radiated Power (ERP) in Watts (optional)
close TX;

# Use TX Longley-Rice parameters for RX also
open(LR, ">", "rx.lrp") or die "Can't open rx.lrp: $!\n";
  print LR "$diecon\n";  # Earth Dielectric Constant (Relative permittivity) - 15.000
  print LR "$earcon\n";  # Earth Conductivity (Siemens per meter) - 0.005
  print LR "$nunits\n";  # Atmospheric Bending Constant (N-units) - 301.000
  print LR "$frq_mhz\n"; # # Frequency in MHz (20 MHz to 20 GHz)
  print LR "$cli\n";     # Radio Climate (5 = Continental Temperate)
  print LR "$ant\n";     # Polarization (0 = Horizontal, 1 = Vertical)
  print LR "$si\n";      # Fraction of situations (50% of locations)
  print LR "$ti\n";      # Fraction of time (90% of the time)
  print LR "0\n";        # Effective Radiated Power (ERP) in Watts (optional)
close TX;

# Run SPLAT!
#
if ($country eq "United States") {
  if ($quality eq "Low / Fast") {

    $qual = "SRTMv3 3 Arc-Second Resolution (Standard)";
    $file1 = sprintf "%s/%.f_%.f_%.f_%.f.sdf", $splatdir, $LAT1_D, ($LAT1_D + 1), $LON1_D, ($LON1_D + 1);
    $file2 = sprintf "%s/%.f_%.f_%.f_%.f.sdf", $splatdir, $LAT2_D, ($LAT2_D + 1), $LON2_D, ($LON2_D + 1);

    if (!-f $file1) {
      print "<p><font color=red><b>Elevation Data Unavailable for: $file1 </b></font></p>\n";
    }
    if (!-f $file2) {
      print "<p><font color=red><b>Elevation Data Unavailable for: $file2 </b></font></p>\n";
    }

	if ($do_div eq "yes") {
      system("$splat -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -gpsav -imperial -kml -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	  system("/bin/mv profile.gp profile1.gp");
      system("/bin/mv reference.gp reference1.gp");
      system("/bin/mv fresnel.gp fresnel1.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61.gp");
	  system("/bin/mv curvature.gp curvature1.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1.gp");
	  system("/bin/mv elevation-clutter.gp elevation-clutter1.gp >/dev/null 2>&1");

	  system("$splat -t tx.qth -r rx-div.qth -p pro1-div -e ElevPro1-div -gc $gc_ft -H PathProfile1-div -l PathLoss1-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile1-div.gp");
      system("/bin/mv reference.gp reference1-div.gp");
      system("/bin/mv fresnel.gp fresnel1-div.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61-div.gp");
      system("/bin/mv curvature.gp curvature1-div.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1-div.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1-div.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter1-div.gp >/dev/null 2>&1");

      system("$splat -t rx-div.qth -r tx.qth -p pro2-div -e ElevPro2-div -gc $gc_ft -H PathProfile2-div -l PathLoss2-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile2-div.gp");
	  system("/bin/mv reference.gp reference2-div.gp");
      system("/bin/mv fresnel.gp fresnel2-div.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_62-div.gp");
	  system("/bin/mv curvature.gp curvature2-div.gp");
      system("/bin/mv elevation-profile.gp elevation-profile2-div.gp");
      system("/bin/mv elevation-reference.gp elevation-reference2-div.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter2-div.gp >/dev/null 2>&1");
      
	  # This is the one used for the TerrainProfile TX to RX
	  system("$splat -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
    elsif ($do_div eq "no") {
      system("$splat -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -gpsav -imperial -kml -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile1.gp");
      system("/bin/mv reference.gp reference1.gp");
      system("/bin/mv fresnel.gp fresnel1.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61.gp");
      system("/bin/mv curvature.gp curvature1.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter1.gp >/dev/null 2>&1");

	  # This is the one used for the TerrainProfile TX to RX
      system("$splat -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m 1 -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
    }
  }
  elsif ($quality eq "High / Slow") {

    $qual = "SRTMv3 1 Arc-Second Resolution (HD)";
    $file1 = sprintf "%s/%.f:%.f:%.f:%.f-hd.sdf", $splatdirhd, $LAT1_D, ($LAT1_D + 1), $LON1_D, ($LON1_D + 1);
    $file2 = sprintf "%s/%.f:%.f:%.f:%.f-hd.sdf", $splatdirhd, $LAT2_D, ($LAT2_D + 1), $LON2_D, ($LON2_D + 1);

    if (!-f $file1) {
      print "<p><font color=red><b>HD Elevation Data Unavailable for: $file1 </b></font></p>\n";
    }
    if (!-f $file2) {
      print "<p><font color=red><b>HD Elevation Data Unavailable for: $file2 </b></font></p>\n";
    }

    if ($do_div eq "no") {
	  system("$splat -hd -sdelim ':' -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -gpsav -imperial -kml -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile1.gp");
      system("/bin/mv reference.gp reference1.gp");
      system("/bin/mv fresnel.gp fresnel1.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61.gp");
      system("/bin/mv curvature.gp curvature1.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter1.gp >/dev/null 2>&1");

      system("$splat -hd -sdelim ':' -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile2-div.gp");
      system("/bin/mv reference.gp reference2-div.gp");
      system("/bin/mv fresnel.gp fresnel2-div.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_62-div.gp");
      system("/bin/mv curvature.gp curvature2-div.gp");
      system("/bin/mv elevation-profile.gp elevation-profile2-div.gp");
      system("/bin/mv elevation-reference.gp elevation-reference2-div.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter2-div.gp >/dev/null 2>&1");
	}
	elsif($do_div eq "yes") {
      system("$splat -hd -sdelim ':' -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -gpsav -imperial -kml -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile1.gp");
      system("/bin/mv reference.gp reference1.gp");
      system("/bin/mv fresnel.gp fresnel1.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61.gp");
      system("/bin/mv curvature.gp curvature1.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter1.gp >/dev/null 2>&1");

      system("$splat  -hd -sdelim ':' -t tx.qth -r rx-div.qth -p pro1-div -e ElevPro1-div -gc $gc_ft -H PathProfile1-div -l PathLoss1-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile1-div.gp");
      system("/bin/mv reference.gp reference1-div.gp");
      system("/bin/mv fresnel.gp fresnel1-div.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_61-div.gp");
      system("/bin/mv curvature.gp curvature1-div.gp");
      system("/bin/mv elevation-profile.gp elevation-profile1-div.gp");
      system("/bin/mv elevation-reference.gp elevation-reference1-div.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter1-div.gp >/dev/null 2>&1");

      system("$splat -hd -sdelim ':' -t rx-div.qth -r tx.qth -p pro2-div -e ElevPro2-div -gc $gc_ft -H PathProfile2-div -l PathLoss2-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("/bin/mv profile.gp profile2-div.gp");
      system("/bin/mv reference.gp reference2-div.gp");
      system("/bin/mv fresnel.gp fresnel2-div.gp");
      system("/bin/mv fresnel_pt_6.gp fresnel_pt_62-div.gp");
      system("/bin/mv curvature.gp curvature2-div.gp");
      system("/bin/mv elevation-profile.gp elevation-profile2-div.gp");
      system("/bin/mv elevation-reference.gp elevation-reference2-div.gp");
      system("/bin/mv elevation-clutter.gp elevation-clutter2-div.gp >/dev/null 2>&1");
	  #
      # This is the one used for the TerrainProfile TX to RX
      system("$splat -hd -sdelim ':'-hd -sdelim ':' -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m 1 -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
  }
}
else {
  # International
  $qual = "SRTMv3 3 Arc-Second Resolution (Standard)";
  if ($do_div eq "yes") {
    system("$splat -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -imperial -gpsav -kml -d $splatdir >/dev/null 2>&1");
    system("/bin/mv profile.gp profile1.gp");
    system("/bin/mv reference.gp reference1.gp");
    system("/bin/mv fresnel.gp fresnel1.gp");
    system("/bin/mv fresnel_pt_6.gp fresnel_pt_61.gp");
    system("/bin/mv curvature.gp curvature1.gp");
    system("/bin/mv elevation-profile.gp elevation-profile1.gp");
    system("/bin/mv elevation-reference.gp elevation-reference1.gp");
    system("/bin/mv elevation-clutter.gp elevation-clutter1.gp >/dev/null 2>&1");

    system("$splat -t tx.qth -r rx-div.qth -p pro1-div -e ElevPro1-div -gc $gc_ft -H PathProfile1-div -l PathLoss1-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir >/dev/null 2>&1");
    system("/bin/mv profile.gp profile1-div.gp");
    system("/bin/mv reference.gp reference1-div.gp");
    system("/bin/mv fresnel.gp fresnel1-div.gp");
    system("/bin/mv fresnel_pt_6.gp fresnel_pt_61-div.gp");
    system("/bin/mv curvature.gp curvature1-div.gp");
    system("/bin/mv elevation-profile.gp elevation-profile1-div.gp");
    system("/bin/mv elevation-reference.gp elevation-reference1-div.gp");
    system("/bin/mv elevation-clutter.gp elevation-clutter1-div.gp >/dev/null 2>&1");

    system("$splat -t rx-div.qth -r tx.qth -p pro2-div -e ElevPro2-div -gc $gc_ft -H PathProfile2-div -l PathLoss2-div -m $k -f $frq_mhz -fz $fres -sc -png -itwom -gpsav -imperial -d $splatdir >/dev/null 2>&1");
    system("/bin/mv profile.gp profile2-div.gp");
    system("/bin/mv reference.gp reference2-div.gp");
    system("/bin/mv fresnel.gp fresnel2-div.gp");
    system("/bin/mv fresnel_pt_6.gp fresnel_pt_62-div.gp");
    system("/bin/mv curvature.gp curvature2-div.gp");
    system("/bin/mv elevation-profile.gp elevation-profile2-div.gp");
    system("/bin/mv elevation-reference.gp elevation-reference2-div.gp");
    system("/bin/mv elevation-clutter.gp elevation-clutter2-div.gp >/dev/null 2>&1");

    system("$splat -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m $k -f $frq_mhz -fz $fres -sc -png -itwom -imperial -gpsav -d $splatdir >/dev/null 2>&1");
  }
  elsif ($do_div eq "no") {
    system("$splat -t tx.qth -r rx.qth -p pro1 -e ElevPro1 -gc $gc_ft -H PathProfile1 -l PathLoss1 -m $k -f $frq_mhz -fz $fres -o TopoMap -sc -png -itwom -imperial -gpsav -kml -d $splatdir >/dev/null 2>&1");
	system("$splat -t rx.qth -r tx.qth -p pro2 -e ElevPro2 -gc $gc_ft -H PathProfile2 -l PathLoss2 -m $k -f $frq_mhz -fz $fres -sc -png -itwom -imperial -gpsav -d $splatdir >/dev/null 2>&1");
  }
}

## Total hack
#
$first = `/usr/bin/head -n 1 profile.gp`;
($a, $tx_elv_ft) = split('\t', $first);
chomp $tx_elv_ft;
$tx_elv_ft = $tx_elv_ft - $tx_ant_ht_ft;
$tx_elv_ft = sprintf "%.2f", $tx_elv_ft;
$tx_elv_m = sprintf "%.2f", $tx_elv_ft * 0.3048;

# Clean up any data gaps
if ($tx_elv_ft eq "-5000.0") {
  $tx_elv_m = sprintf "%.2f", 0;
  $tx_elv_ft = sprintf "%.2f", 0;
}

$last = `/usr/bin/tail -n 1 profile.gp`;
($a, $rx_elv_ft) = split('\t', $last);
chomp $rx_elv_ft;
$rx_elv_ft = $rx_elv_ft - $rx_ant_ht_ft;
$rx_elv_ft = sprintf "%.2f", $rx_elv_ft;
$rx_elv_m = sprintf "%.2f", $rx_elv_ft * 0.3048;

# Clean up any data gaps
if ($rx_elv_ft eq "-5000.0") {
  $rx_elv_m = sprintf "%.2f", 0;
  $rx_elv_ft = sprintf "%.2f", 0;
}

# Get antenna height above AMSL
$tx_ant_ht_ov_m = sprintf "%.2f", $tx_elv_m + $tx_ant_ht_m;
$rx_ant_ht_ov_m = sprintf "%.2f", $rx_elv_m + $rx_ant_ht_m;
$tx_ant_ht_ov_ft = sprintf "%.2f", $tx_elv_ft + $tx_ant_ht_ft;
$rx_ant_ht_ov_ft = sprintf "%.2f", $rx_elv_ft + $rx_ant_ht_ft;

# Subtract TX and RX antenna heights from elevation data
open(F, ">", "elev1") or die "Can't open elev1: $!\n";
  $first = `head -n 1 profile.gp`;
  ($a, $b) = split('\t', $first);
  chomp $b;
  $b = $b - $tx_ant_ht_ft;
  print F "$a\t$b\n";
close F;

&System($args = "/usr/bin/tail -n +2 profile.gp >> elev1");

$last = `tail -n 1 profile.gp`;
($a, $b) = split('\t', $last);
chomp $b;
$b = $b - $rx_ant_ht_ft;

&System($args = "/usr/bin/head -n -1 elev1 > profile2.gp");

open(F, ">>", "profile2.gp") or die "Can't open elev2: $!\n";
  print F "$a\t$b\n";
close F;

# Average height, minimum height, maximum height
system("/usr/bin/sed -e '1d' -e '\$d' profile.gp > average.gp"); # skip first and last lines to get fake antenna elevations

open(F, "<", "average.gp") || die "Can't open average.gp: $!\n";
  chomp(my @AVG = <F>);
close F;

foreach (@AVG) {
  ($x, $y) = split;
  push (@DIST, $x);
  push (@ELEV, $y);
}

## Sort the array
#
use List::Util qw(min max);
$max_dist = max(@DIST);
$min_elev = min(@ELEV);
$max_elev = max(@ELEV);

$count = 0;
$ee = 0;
$e = 0;

foreach $e (@ELEV) {
  $ee += $e;
  $count++;
}

$avg_ht_ft = sprintf "%.2f", ($ee / $count);
$avg_ht_m = sprintf "%.2f", ($ee / $count) * 0.3048;
$min_elev_ft = sprintf "%.2f", $min_elev;
$min_elev_m = sprintf "%.2f", $min_elev * 0.3048;
$max_elev_ft = sprintf "%.2f", $max_elev;
$max_elev_m = sprintf "%.2f", $max_elev * 0.3048;

## Earth Bulge
#
if ($k_str eq "Infinity") {
  $bulge_ft = sprintf "%.2f", 0;
  $bulge_m  = sprintf "%.2f", 0;
}
else {
  $bulge    = ($dist_mi / 2) * ($dist_mi / 2) / (1.5 * $k);
  $bulge_ft = sprintf "%.2f", $bulge;
  $bulge_m  = sprintf "%.2f", $bulge_ft * 0.3048;
}

## Maximum Fresnel Zone Radius
#
$max_fres_m  = sprintf "%.2f", 17.34 * sqrt($dist_km / (4 * $frq_ghz));
$max_fres_ft = sprintf "%.2f", (17.34 * sqrt($dist_km / (4 * $frq_ghz))) / 0.3048;

## Obstruction Arrows on Terrain Graph (Only First 5) 
# 
$obs_count = 5;

open(F, "<", "$rx_name-to-$tx_name.txt") or die "Can't open file $rx_name-to-$tx_name.txt: $!\n";
while (<F>) {
  chomp;
  if ($obs_count > 0) {
    if (/OBS:/) {
      ($z, $y, $x, $w, $v) = split '>';
      $w =~ tr/0-9.//csd;
      push (@OBS, $w);
      $obs_count--;
    }
  }
}
close F;

$obs1 = shift @OBS;
$obs2 = shift @OBS;
$obs3 = shift @OBS;
$obs4 = shift @OBS;
$obs5 = shift @OBS;

## Get ITM Path Loss Value - Primary
#
open(F, "<", "$rx_name-to-$tx_name.txt") or die "Can't open file $rx_name-to-$tx_name.txt: $!\n";
  while (<F>) {
    chomp;
    if (/ITWOM Version/) {
      ($z, $y, $x, $w, $v) = split '>';
      $w =~ tr/0-9.//csd;
      $itm = sprintf "%.2f", $w;
    }
  }
close F;

## Get ITM Path Loss Value - Diversity
#
if ($do_div eq "yes") {
  open(F, "<", "$rx_div_name-to-$tx_name.txt") or die "Can't open file $rx_div_name-to-$tx_name.txt: $!\n";
    while (<F>) {
      chomp;
      if (/ITWOM Version/) {
        ($z, $y, $x, $w, $v) = split '>';
        $w =~ tr/0-9.//csd;
        $div_itm = sprintf "%.2f", $w;
      }
    }
  close F;
}
elsif ($do_div eq "no") {
  $div_itm      = sprintf "%.2f", 0;
  $div_itm_rain = sprintf "%.2f", 0;
}

## Generate Approximate ITM Path Loss Coverage at TX
#
$pathdist = sprintf "%.f", ($max_dist + 10);

if ($country eq "United States") {
  if ($quality eq "Low / Fast") {
    system("$splat -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap1 -sc -png -imperial -itwom -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	if ($do_div eq "no") {
      system("$splat -t rx.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
	elsif ($do_div eq "yes") {
	  system("$splat -t rx.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	  system("$splat -t rx-div.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap-div -sc -png -imperial -itwom -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
  }	
  elsif ($quality eq "High / Slow") {
    if ($do_div eq "no") {
      system("$splat -hd -sdelim ':' -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap1 -sc -png -imperial -itwom -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("$splat -hd -sdelim ':' -t rx.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
    }
    elsif ($do_div eq "yes") { 
      system("$splat -hd -sdelim ':' -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap1 -sc -png -imperial -itwom -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("$splat -hd -sdelim ':' -t rx.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("$splat -hd -sdelim ':' -t rx-div.qth -L $rx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap-div -sc -png -imperial -itwom -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
    }
  }
}
else {
  # International
  if ($do_div eq "no") {
    system("$splat -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap1 -sc -png -imperial -itwom -d $splatdir >/dev/null 2>&1");
    system("$splat -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdir >/dev/null 2>&1");
  }
  if ($do_div eq "yes") {
    system("$splat -t tx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap1 -sc -png -imperial -itwom -d $splatdir >/dev/null 2>&1");
    system("$splat -t rx.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap2 -sc -png -imperial -itwom -d $splatdir >/dev/null 2>&1");
    system("$splat -t rx-div.qth -L $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LossMap-div -sc -png -imperial -itwom -d $splatdir >/dev/null 2>&1");
  }
}

## Generate Line-of-Sight Coverage at TX and RX
#
if ($country eq "United States") {
  if ($quality eq "Low / Fast") {
    if ($do_div eq "no") {
      system("$splat -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
	elsif ($do_div eq "yes") {
	  system("$splat -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	  system("$splat -t tx.qth rx-div.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap-div -sc -png -imperial -d $splatdir -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
  }
  elsif ($quality eq "High / Slow") {
	if ($do_div eq "no") {
      system("$splat -hd -sdelim ':' -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
	elsif ($do_div eq "yes") {
	  system("$splat -hd -sdelim ':' -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
      system("$splat -hd -sdelim ':' -t tx.qth rx-div.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap-div -sc -png -imperial -d $splatdirhd -s $splatdir/$cities -b $splatdir/$counties >/dev/null 2>&1");
	}
  }
}
else {
  # International
  if ($do_div eq "no") {
    system("$splat -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdir >/dev/null 2>&1");
  }
  elsif ($do_div eq "yes") {
    system("$splat -t tx.qth rx.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap -sc -png -imperial -d $splatdir >/dev/null 2>&1");
	system("$splat -t tx.qth rx-div.qth -c $tx_ant_ht_ft -m $k -R $pathdist -gc $gc_ft -o LOSMap-div -sc -png -imperial -d $splatdir >/dev/null 2>&1");
  }
}

## Approx. Antenna 3 dB Beamwidth
#
$tx_ant_bw = sprintf "%.2f", 164 * sqrt(1 / (10 ** ($tx_ant_gain_dbi / 10)));
$rx_ant_bw = sprintf "%.2f", 164 * sqrt(1 / (10 ** ($rx_ant_gain_dbi / 10)));

## Calculate azimuths
#
$lat1_az = deg2rad($LAT1);
$lon1_az = deg2rad($LON1 * -1);
$lat2_az = deg2rad($LAT2);
$lon2_az = deg2rad($LON2 * -1);

$cosd = sin($lat2_az) * sin($lat1_az) + cos($lat1_az) * cos($lat2_az) * cos($lon1_az - $lon2_az);
$daz = rad2deg(acos $cosd);
$cosb = (sin($lat2_az) - sin($lat1_az) * cos(deg2rad($daz))) / (cos($lat1_az) * sin(deg2rad($daz)));

if ($cosb > 0.999999) {
  $AZ = 0;
}
elsif ($cosb < -0.999999) {
  $AZ = 180;
}
else {
  $AZ = rad2deg(acos $cosb);
}

if (sin($lon2_az - $lon1_az) >= 0) {
  $AZSP = $AZ;
  $AZLP = 180 + $AZ;
}
else {
  $AZSP = 360 - $AZ;
  $AZLP = 180 - $AZ;
}

$AZSP = sprintf "%.2f", $AZSP; # TX to RX - TN
$AZLP = sprintf "%.2f", $AZLP; # RX to TX - TN

# Calculate Magnetic Declination
#
# Requires the installation of pygeomag: https://github.com/boxpet/pygeomag
#
if ($do_mag eq "yes") {
  $day_of_year = localtime->yday + 1;
  $dec_date    = sprintf "%.2f", $year + ($day_of_year / 365);

  # TX Site
  open(F, ">", "magdec.py") or die "Can't open magdec.py: $!\n";
    print F "from pygeomag import GeoMag\n";
    print F "geo_mag = GeoMag()\n";
    print F "result = geo_mag.calculate(glat=$LAT1, glon=$LON1_geo, alt=0, time=$dec_date)\n";
    print F "print(result.d)\n";
  close F;

  chomp($value1 = `/usr/bin/python3 ./magdec.py`);
  $magdec_tx = sprintf "%.2f", $value1;

  if ($magdec_tx < 0) {
    $magdir_tx = "West";
	$AZSP_MN = sprintf "%.2f", $AZSP + abs($magdec_tx);
	
	if ($AZSP_MN >= 360) {
	  $AZSP_MN = sprintf "%.2f", $AZSP_MN - 360;
	}
  }
  else {
    $magdir_tx = "East";
	$AZSP_MN = sprintf "%.2f", $AZSP - abs($magdec_tx);

    if ($AZSP_MN < 0) {
      $AZSP_MN = sprintf "%.2f", $AZSP_MN + 360;
    }
  }

  $magdec_tx = abs($magdec_tx);

  # RX Site
  open(F, ">", "magdec.py");
    print F "from pygeomag import GeoMag\n";
    print F "geo_mag = GeoMag()\n";
    print F "result = geo_mag.calculate(glat=$LAT2, glon=$LON2_geo, alt=0, time=$dec_date)\n";
    print F "print(result.d)\n";
  close F;

  chomp($value2 = `/usr/bin/python3 ./magdec.py`);
  $magdec_rx = sprintf "%.2f", $value2;

  if ($magdec_rx < 0) {
    $magdir_rx = "West";
    $AZLP_MN = sprintf "%.2f", $AZLP + abs($magdec_rx);

    if ($AZLP_MN >= 360) {
      $AZLP_MN = sprintf "%.2f", $AZLP_MN - 360;
    }

  }
  else {
    $magdir_rx = "East";
	$AZLP_MN = sprintf "%.2f", $AZLP - abs($magdec_rx);

	if ($AZLP_MN < 0) {
      $AZLP_MN = sprintf "%.2f", $AZLP_MN + 360;
    }
  }

  $magdec_rx = abs($magdec_rx);
}
elsif ($do_mag eq "no") {
  $magdec_tx = "Not Calculated";
  $magdir_tx = "";
  $magdec_rx = "Not Calculated";
  $magdir_rx = "";
}

## Misc Stuff I Forgot
#
if ($do_div eq "no") {
  $div_rx_ant_ht_ov_ft = "Not Applicable";
  $div_rx_ant_ht_ov_m =  "N/A";
  }
elsif ($do_div eq "yes") {
  $div_rx_ant_ht_ov_ft = sprintf "%.2f", $rx_elv_ft + $div_ant_ht_ft;
  $div_rx_ant_ht_ov_m = sprintf "%.2f", $rx_elv_m + $div_ant_ht_m;
}

## Calculate Antenna Tilt
#
#$TR = (180 / pi) * ((($rx_ant_ht_ov_ft - $tx_ant_ht_ov_ft) / (5280 * $dist_mi)) - ($dist_mi / (7920 * $k)));
#$RT = (180 / pi) * ((($tx_ant_ht_ov_ft - $rx_ant_ht_ov_ft) / (5280 * $dist_mi)) - ($dist_mi / (7920 * $k)));
if ($do_div eq "no") {
  $tilt = rad2deg(atan(($tx_ant_ht_ov_ft - $rx_ant_ht_ov_ft) / ((5280 * $dist_mi) - ($dist_mi / 7920 * $k))));
  $tilt_rtd = sprintf "%.2f", 0
}
elsif ($do_div eq "yes") {
  $tilt     = rad2deg(atan(($tx_ant_ht_ov_ft - $rx_ant_ht_ov_ft) / ((5280 * $dist_mi) - ($dist_mi / 7920))));
  $tilt_div = rad2deg(atan(($tx_ant_ht_ov_ft - $div_rx_ant_ht_ov_ft) / ((5280 * $dist_mi) - ($dist_mi / 7920))));

  if ($tilt_div < 0) {
    $tilt_rtd = sprintf "-%.2f", abs($tilt_div);
  }
  elsif ($tilt_div > 0) {
	$tilt_rtd = sprintf "+%.2f", abs($tilt_div);
  }
} 

if ($tilt < 0) {
  # TX is higher than RX, so make tilt UPWARD
  $tilt_tr = sprintf "+%.2f", abs($tilt);
  $tilt_rt = sprintf "-%.2f", abs($tilt);
  # Determine the inner radius of the coverage area, helping you understand the closer range of the signal.
  $inner = ($tx_ant_ht_ov_ft / tan(deg2rad(abs($tilt)) + deg2rad($tx_ant_bw) / 2)) / 5280;
  # Calculate the outer radius of the coverage area, providing insight into the maximum reach of your antenna’s signal.
  $outer = ($tx_ant_ht_ov_ft / tan(deg2rad(abs($tilt)) - deg2rad($tx_ant_bw) / 2)) / 5280;
  $inner = sprintf "%.2f", $inner;
  $outer = sprintf "%.2f", $outer;

  if ($outer <= 0 || $outer > $dist_mi) {
    $outer = "Horizon";
  }

  if ($inner <= 0) {
    $inner = "Error";
  }

}
elsif ($tilt > 0) {
  # TX is lower than RX, so make tilt DOWNWARD
  $tilt_tr = sprintf "-%.2f", abs($tilt);
  $tilt_rt = sprintf "+%.2f", abs($tilt);
  # Determine the inner radius of the coverage area, helping you understand the closer range of the signal.
  $inner = ($tx_ant_ht_ov_ft / tan(deg2rad($tilt) + deg2rad($tx_ant_bw) / 2)) / 5280;
  # Calculate the outer radius of the coverage area, providing insight into the maximum reach of your antenna’s signal.
  $outer = ($tx_ant_ht_ov_ft / tan(deg2rad($tilt) - deg2rad($tx_ant_bw) / 2)) / 5280;
  $inner = sprintf "%.2f", $inner;
  $outer = sprintf "%.2f", $outer;

  if ($outer <= 0) {
    # Horizon means that the -3dB point on the main lobe shoots off into the horizon and does not touch the earth (assuming flat terrain.)
    $outer = "Horizon";
  }
}

## Plot Fancy Terrain Profile: TX to RX
#
open(F1, "<", "profile2.gp") or die "Can't open file profile2.gp: $!\n";
open(F2, ">", "profile-k.gp") or die "Can't open file profile-k.gp: $!\n";
open(F3, ">", "profile-terr.gp") or die "Can't open file profile-terr.gp: $!\n";
  while (<F1>) {
    chomp;
    ($dist, $elev) = split(/\t/);
    $d1 = $dist_mi - $dist;
    $d2 = ($dist_mi + $dist) - $dist_mi;
    $ht =  ($d1 * $d2) / (1.5 * $k);
	$new = sprintf "%.6f", $elev - $ht; # subtract earth k-factor from terrain data
    print F2 "$dist\t$new\n";
	print F3 "$dist\t$elev\n";
}
close F1;
close F2;
close F3;

if ($do_div eq "yes") {
  open(F1, "<", "reference2-div.gp") or die "Can't open file reference2-div.gp: $!\n";
    while (<F1>) {
    chomp(@REFDIV = <F1>);
  }
  close F1;

  foreach (@REFDIV) {
    ($dist, $elev) = split;
    push(@REFDIV_DIST, $dist);
    push(@REFDIV_ELEV, $elev);
  }

  $size = (@REFDIV_DIST);
  $count = 1;

  open(F2, ">", "fresnel-div-nth.gp");
    while ($count < $size) {
      $dist = shift(@REFDIV_DIST);
      $elev = shift(@REFDIV_ELEV);
      $d1 = $dist;
      $d2 = $dist_mi - $d1;
      $fn = sprintf "%.6f", 72.05 * ($fres/100) * sqrt(($d1 * $d2) / ($frq_ghz * $dist_mi));
      $new = sprintf "%.6f", $elev - abs($fn);
      print F2 "$d1\t$new\n";
      $count++;                                                                                                                                                                     
    }
  close F2;
}

## Calculate Terrain Roughness Factor
#
open(TER, "<", "profile2.gp") or die "Can't open file profile2.gp: $!\n";
while (<TER>) {
  chomp;
  ($a, $b) = split;
  push(@ELEV_ARRAY, $b);
}
close TER;

# Remove end point data
while ($i < 5) {
  $tmp = shift(@ELEV_ARRAY);
  $tmp = pop(@ELEV_ARRAY);
  $i++;
}

$ter_count = scalar(@ELEV_ARRAY);
$ter_size  = scalar(@ELEV_ARRAY);

if (!$ter_size) {
  $size = 10; # Divide-by-zero catch
}

while($ter_count > 0) {
  $elev = shift(@ELEV_ARRAY);
  $Eds  = $Eds + $elev;
  $Esq  = $Esq + ($elev ** 2);
  $ter_count--;
}

$ter_w = sqrt(abs(($Esq / $ter_size) - (($Eds / $ter_size) ** 2)));

$rough_calc_ft   = sprintf "%.1f", $ter_w;
$rough_calc_m    = sprintf "%.1f", $ter_w * 0.3048;

## Plot Terrain Profile
#
open(F, ">", "splat2.gp") or die "Can't open splat2.gp: $!\n";
  print F "set clip\n";
  print F "set tics scale 2, 1\n";
  print F "set mytics 10\n";
  print F "set mxtics 20\n";
  print F "set tics out\n";
  print F "set border 3\n";
  print F "set label 1 '\\U+1F985'\n"; # eagle
  print F "set label 2 '\\U+1F983'\n"; # turkey
  print F "set label 3 '\\U+1F6F8'\n"; # ufo
  print F "set label 4 '\\U+1F986'\n"; # duck
  $eagle  = sprintf "%.2f", rand(0.87-0.60) + 0.61;
  $turkey = sprintf "%.2f", rand(0.81-0.55) + 0.54;
  $duck   = sprintf "%.2f", rand(0.79-0.40) + 0.41;
  print F "set label 1 at screen 0.5, screen $eagle font ',30'\n";
  print F "set label 2 at screen 0.35, screen $turkey font ',30'\n";
  print F "set label 3 at screen 0.015, screen 0.97 font ',30'\n";
  print F "set label 4 at screen 0.65, screen $duck font ',30'\n";
  print F "set key below enhanced font \"Helvetica,18\"\n";
  print F "set grid back xtics ytics mxtics mytics\n";

  if ($tx_ant_ht_ov_ft > $rx_ant_ht_ov_ft) {
    $ymax = $tx_ant_ht_ov_ft + $div_ft;
  }
  else {
    $ymax = $rx_ant_ht_ov_ft + $div_ft + 5;
  } 
 
  if ($max_elev_ft > $ymax) {
    $ymax = $max_elev_ft;
  }

  print F "set yrange [($min_elev - 5) to ($ymax + 10)]\n";
  print F "set xrange [0.0 to $dist_mi]\n";
  print F "set encoding utf8\n";
  print F "set samples 500\n";
  print F "set term pngcairo enhanced size 2000,1600\n";
  print F "set title \"{/:Bold Path Profile Between $tx_name and $rx_name\\n$qual }\" font \"Helvetica,30\"\n";
  print F "set xlabel \"Distance Between {/:Bold $tx_name } and {/:Bold $rx_name } ($dist_mi miles)\\n\" font \"Helvetica,22\"\n";
  print F "set x2label \"Frequency: $frq_mhz MHz\t\tAzimuth: $AZSP\\U+00B0 TN / $AZSP_MN\\U+00B0 MN  ($AZLP\\U+00B0 TN / $AZLP_MN\\U+00B0 MN)\" font \"Helvetica,20\"\n";
  print F "set ylabel \"Elevation - Above Mean Sea Level (feet)\" font \"Helvetica,22\"\n";
  print F "set arrow from 0,$tx_elv_ft to 0,$tx_ant_ht_ov_ft head lw 3 size screen 0.008,45.0,30.0 filled\n";
  print F "set arrow from $dist_mi,$rx_elv_ft to $dist_mi,$rx_ant_ht_ov_ft head lw 3 size screen 0.008,45.0,30.0 filled\n";

  if ($do_div eq "yes") {
	my $a = $rx_ant_ht_ov_ft + $div_ft;
    print F "set arrow from $dist_mi,$rx_ant_ht_ov_ft to $dist_mi,$a head lw 3 size screen 0.008,40.0,30.0 filled\n";
	print F "set label \"Div. $a     \\n\\n\" right front at $dist_mi,$a\n";
  }

  if ($obs1) {
    print F "set arrow from $obs1,$min_elev to $obs1,$avg_ht_ft lw 2\n";
  }
  if ($obs2) {
    print F "set arrow from $obs2,$min_elev to $obs2,$avg_ht_ft lw 2\n";
  }
  if ($obs3) {
    print F "set arrow from $obs3,$min_elev to $obs3,$avg_ht_ft lw 2\n";
  }
  if ($obs4) {
    print F "set arrow from $obs4,$min_elev to $obs4,$avg_ht_ft lw 2\n";
  }
  if ($obs5) {
    print F "set arrow from $obs5,$min_elev to $obs5,$avg_ht_ft lw 2\n";
  }

  print F "set label \"     $tx_ant_ht_ov_ft\" left front at 0,$tx_ant_ht_ov_ft\n";
  print F "set label \"Pri. $rx_ant_ht_ov_ft     \" right front at $dist_mi,$rx_ant_ht_ov_ft\n";
  print F "set label 'Lat: $LAT1_D\\U+00B0 $LAT1_M\\U+0027 $LAT1_S\" $LAT1_gnu' left at 0,graph 1.07\n";
  print F "set label 'Lon: $LON1_D\\U+00B0 $LON1_M\\U+0027 $LON1_S\" $LON1_gnu' left at 0,graph 1.05\n";
  print F "set label 'Gnd Elv: $tx_elv_ft ft' left at 0,graph 1.03\n";
  print F "set label 'Ant Hgt: $tx_ant_ht_ft ft' left at 0,graph 1.01\n";
  print F "set label 'Lat: $LAT2_D\\U+00B0 $LAT2_M\\U+0027 $LAT2_S\" $LAT2_gnu' right at $dist_mi,graph 1.07\n";
  print F "set label 'Lon: $LON2_D\\U+00B0 $LON2_M\\U+0027 $LON2_S\" $LON2_gnu' right at $dist_mi,graph 1.05\n";
  print F "set label 'Gnd Elv: $rx_elv_ft ft' right at $dist_mi,graph 1.03\n";
  print F "set label 'Ant Hgt: $rx_ant_ht_ft ft' right at $dist_mi,graph 1.01\n";
  print F "set timestamp '%d-%b-%Y %H:%M CST' bottom font \"Helvetica\"\n";
  print F "set output \"TerrainProfile.png\"\n";
  print F "set style fill transparent solid 0.6 border -1\n";

  if ($clutter == 1) {
    # Do clutter
	if ($do_div eq "yes") {
      # Do clutter and diversity antenna
      print F "plot \"profile-terr.gp\" title \"$k_str Earth Terrain Profile\" with filledcurves above fc \"grey80\", \"profile-k.gp\" title \"1/1 Earth Terrain Profile\" with filledcurves above fc \"brown\", \"reference.gp\" title \"Pri. Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\", \"fresnel.gp\" smooth csplines title \"Pri. First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"green\", \"fresnel_pt_6.gp\" smooth csplines title \"Pri. $fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\", \"clutter.gp\" title \"$gc_ft ft Additional Ground Clutter\" with lines lt 1 lw 2 linecolor rgb 'black' dashtype 3, \"reference-div.gp\" title \"Div. Reference Path\" with line lt 1 lw 1 linecolor rgb \"blue\" dashtype 5\n";
    }
	elsif ($do_div eq "no") {
	  # Do clutter, no diversity antenna
	  print F "plot \"profile-terr.gp\" title \"$k_str Earth Terrain Profile\" with filledcurves above fc \"grey80\", \"profile-k.gp\" title \"1/1 Earth Terrain Profile\" with filledcurves above fc \"brown\", \"reference.gp\" title \"Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\", \"fresnel.gp\" smooth csplines title \"First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"green\", \"fresnel_pt_6.gp\" smooth csplines title \"$fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\", \"clutter.gp\" title \"$gc_ft ft Additional Ground Clutter\" with lines lt 1 lw 2 linecolor rgb 'black' dashtype 3\n";
	}
  }
  elsif ($clutter == 0) {
    # No clutter
    if ($do_div eq "yes") {
	  # No clutter, but with diversity antenna
      print F "plot \"profile-terr.gp\" title \"$k_str Earth Terrain Profile\" with filledcurves above fc \"grey80\", \"profile-k.gp\" title \"1/1 Earth Terrain Profile\" with filledcurves above fc \"brown\", \"reference.gp\" title \"Pri. Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\", \"fresnel.gp\" smooth csplines title \"Pri. First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"green\", \"fresnel_pt_6.gp\" smooth csplines title \"Pri. $fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\", \"reference2-div.gp\" title \"Div. Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\" dashtype 5, \"fresnel-div-nth.gp\" smooth csplines title \"Div. $fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\" dashtype 5\n";
     }
	 elsif ($do_div eq "no") {
	  # No clutter, no diversity antenna
	  print F "plot \"profile-terr.gp\" title \"$k_str Earth Terrain Profile\" with filledcurves above fc \"grey80\", \"profile-k.gp\" title \"1/1 Earth Terrain Profile\" with filledcurves above fc \"brown\", \"reference.gp\" title \"Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\", \"fresnel.gp\" smooth csplines title \"First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"green\", \"fresnel_pt_6.gp\" smooth csplines title \"$fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\"\n";
     }
  }
close F;

&System($args = "$gnuplot splat2.gp >/dev/null 2>&1");

## Climate & Terrain Factors
#
# check4 = Would You Like to Calculate the Vigants-Barnett Climate Factor?
$rough =~ tr/0-9.//csd;

if ($check4 eq "yes") {
  if ($rough_val eq "meters") {
    $rough_m = sprintf "%.1f", $rough;
    $rough_ft = sprintf "%.1f", $rough / 0.3048;
  }
  else {
    $rough_m = sprintf "%.1f", $rough * 0.3048;
    $rough_ft = sprintf "%.1f", $rough;
  }

  if ($rough_ft < 20) {
    $rough_ft = sprintf "%.1f", 20;
    $rough_m = sprintf "%.1f", 20 * 0.3048;
  }

  if ($rough_ft > 140) {
    $rough_ft = sprintf "%.1f", 140;
    $rough_m = sprintf "%.1f", 140 * 0.3048;
  }
}

if ($check4 eq "yes") {
  if ($rough_hum eq "Coastal, Very Humid Areas") {
    $cli_vig = sprintf "%.2f", 2.0 * (($rough_ft / 50) ** -1.3);
	$cli_val = "Calculated";
  }
  elsif ($rough_hum eq "Non-Coastal, Humid Areas") {
	$cli_vig = sprintf "%.2f", 1.4 * (($rough_ft / 50) ** -1.3);
	$cli_val = "Calculated";
  }
  elsif ($rough_hum eq "Average or Temperate Areas") {
    $cli_vig = sprintf "%.2f", 1.0 * (($rough_ft / 50) ** -1.3);
    $cli_val = "Calculated"
  }
  elsif ($rough_hum eq "Dry Areas") {
    $cli_vig = sprintf "%.2f", 0.5 * (($rough_ft / 50) ** -1.3);
    $cli_val = "Calculated"
  }
}
elsif ($check4 eq "no") {
  $rough_ft = sprintf "%.1f", 50;
  $rough_m = sprintf "%.1f", 50 * 0.3048;
  $rough_hum = "Average or Temperate Areas";

  if ($vigants eq "6.00 : Very smooth terrain, over water or flat desert, coastal") {
    $cli_vig = sprintf "%.2f", 6.00;
    ($null, $vig_val) = split ':', $vigants;
    $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
	$cli_val = "Supplied";
  }
  elsif ($vigants eq "4.00 : Very smooth terrain, over water or flat desert, non-coastal") {
    $cli_vig = sprintf "%.2f", 4.00;
   ($null, $vig_val) = split ':', $vig_val;
   $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
   $cli_val = "Supplied";
  }
  elsif ($vigants eq "2.00 : Great Lakes area") {
    $cli_vig = sprintf "%.2f", 2.00;
   ($null, $vig_val) = split ':', $vigants;
   $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
   $cli_val = "Supplied";
  }
  elsif ($vigants eq "1.00 : Average terrain, with some roughness") {
    $cli_vig = sprintf "%.2f", 1.00;
    ($null, $vig_val) = split ':', $vigants;
    $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
	$cli_val = "Supplied";
  }
  elsif ($vigants eq "0.50 : Dry desert climate") {
    $cli_vig = sprintf "%.2f", 0.50;
    ($null, $vig_val) = split ':', $vigants;
    $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
	$cli_val = "Supplied";
  }
  elsif ($vigants eq "0.25 : Mountainous, very rough, very dry but non-reflective") {
    $cli_vig = sprintf "%.2f", 0.25;
    ($null, $vig_val) = split ':', $vigants;
    $vig_val = substr ($vig_val, 1, ((length $vig_val) - 1));
	$cli_val = "Supplied";
  }
}

## Distance to Radio Horizon
#
if ($k_str eq "Infinity") {
  $tx_rad_hor_mi = (sqrt(2 * 20925721.784777 * 1 * $tx_ant_ht_ft)) / 5280;
  $rx_rad_hor_mi = (sqrt(2 * 20925721.784777 * 1 * $rx_ant_ht_ft)) / 5280;
  $tx_rad_hor_km = sprintf "%.2f", $tx_rad_hor_mi * 1.609344; # distance (km) to radio horizon
  $rx_rad_hor_km = sprintf "%.2f", $rx_rad_hor_mi * 1.609344; # distance (km) to radio horizon
  $tx_rad_hor_mi = sprintf "%.2f", $tx_rad_hor_mi;
  $rx_rad_hor_mi = sprintf "%.2f", $rx_rad_hor_mi;
}
else {
  $tx_rad_hor_mi = (sqrt(2 * 20925721.784777 * $k * $tx_ant_ht_ft)) / 5280;
  $rx_rad_hor_mi = (sqrt(2 * 20925721.784777 * $k * $rx_ant_ht_ft)) / 5280;
  $tx_rad_hor_km = sprintf "%.2f", $tx_rad_hor_mi * 1.609344; # distance (km) to radio horizon
  $rx_rad_hor_km = sprintf "%.2f", $rx_rad_hor_mi * 1.609344; # distance (km) to radio horizon
  $tx_rad_hor_mi = sprintf "%.2f", $tx_rad_hor_mi;
  $rx_rad_hor_mi = sprintf "%.2f", $rx_rad_hor_mi;
}

## Maximum Communication Distance
#
$distance_max_km = sprintf "%.2f", $tx_rad_hor_km + $rx_rad_hor_km;
$distance_max_mi = sprintf "%.2f", $tx_rad_hor_mi + $rx_rad_hor_mi;

$tx_ant_ht_ov_ft = sprintf "%.2f", $tx_ant_ht_ft + $tx_elv_ft;
$tx_ant_ht_ov_m  = sprintf "%.2f", $tx_ant_ht_m + $tx_elv_m;
$rx_ant_ht_ov_ft = sprintf "%.2f", $rx_ant_ht_ft + $rx_elv_ft;
$rx_ant_ht_ov_m  = sprintf "%.2f", $rx_ant_ht_m + $rx_elv_m;

## Cable Loss per Meter
#
sub Cable {
  undef $loss_per_foot; undef $loss_per_meter; undef $cab_desc;
  if ($val eq "Times Microwave LMR-200") {
    $loss_per_foot = (2.8654 + 0.006543 * $frq_mhz) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
    $cab_desc = "3/16\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-240") {
    $loss_per_foot = (2.1554 + 0.005048 * $frq_mhz) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
    $cab_desc = "1/4\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-400") {
    $loss_per_foot = ((0.12229 * sqrt $frq_mhz) + (0.00026 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "3/8\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-400 UltraFlex") {
    $loss_per_foot = ((0.12229 * sqrt $frq_mhz) + (0.00026 * $frq_mhz)) / 100;
    $loss_per_foot = $loss_per_foot + ($loss_per_foot * 0.15);
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "3/8\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-500") {
    $loss_per_foot = ((0.09659 * sqrt $frq_mhz) + (0.00026 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "1/2\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-600") {
    $loss_per_foot = ((0.0755 * sqrt $frq_mhz) + (0.00026 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "1/2\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-900") {
    $loss_per_foot = ((0.05177 * sqrt $frq_mhz) + (0.00016 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "5/8\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-1200") {
    $loss_per_foot = ((0.03737 * sqrt $frq_mhz) + (0.00016 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "7/8\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Times Microwave LMR-1700") {
    $loss_per_foot = ((0.02646 * sqrt $frq_mhz) + (0.00016 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
	$cab_desc = "1-1/4\" Foam Dielectric 50-ohm";
  }
  elsif ($val eq "Andrew HELIAX LDF2-50") {
	if ($frq_mhz <= 13000) {
      $loss_per_foot = (1.5271 + 0.001232 * $frq_mhz) / 100;
	  $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "3/8\" Foam Dielectric 50-ohm";
	}
    else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
	}
  } 
  elsif ($val eq "Andrew HELIAX LDF4.5-50") {
    if ($frq_mhz <= 6100) {
      $loss_per_foot = (0.5348 + 0.0008228 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "5/8\" Low-Density Foam 50-ohm";
    }
	else {
	  $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  } 
  elsif ($val eq "Andrew HELIAX LDF4-50A") {
	if ($frq_mhz <= 8800) {
      $loss_per_foot = ((0.06432 * sqrt $frq_mhz) + (0.00019 * $frq_mhz)) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
	  $cab_desc = "1/2\" Foam Dielectric 50-ohm";
	}
	else {
	  $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX LDF5-50A") {
    if ($frq_mhz <= 5000) {
      $loss_per_foot = ((0.03482 * sqrt $frq_mhz) + (0.00015 * $frq_mhz)) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
  	  $cab_desc = "7/8\" Foam Dielectric 50-ohm";
    }
    else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX LDF6-50A") {
    if ($frq_mhz <= 3300) {
      $loss_per_foot = ((0.02397 * sqrt $frq_mhz) + (0.00014 * $frq_mhz)) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
	  $cab_desc = "1-1/4\" Foam Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX LDF7-50A") {
    if ($frq_mhz <= 2700) {
      $loss_per_foot = ((0.01901 * sqrt $frq_mhz) + (0.00014 * $frq_mhz)) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
	  $cab_desc = "1-5/8\" Foam Dielectric 50-ohm";
    }
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX FSJ1-50") {
	if ($frq_mhz <= 18000) {
	  $loss_per_foot = (3.0024 + 0.00236 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "1/4\" Flexible Foam Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  } 
  elsif ($val eq "Andrew HELIAX FSJ4-50B") {
    if ($frq_mhz <= 10200) {
      $loss_per_foot = (1.3738 + 0.00146 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "1/2\" Flexible Foam Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
   elsif ($val eq "Andrew HELIAX HT4-50") {
     if ($frq_mhz <= 10900) {
       $loss_per_foot = (1.1679 + 0.001518 * $frq_mhz) / 100;
       $loss_per_meter = $loss_per_foot * 3.2808399;
       $cab_desc = "1/2\" High-Temp Foam Dielectric 50-ohm";
	 }
	 else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HT5-50") {
	if ($frq_mhz <= 5000) {
      $loss_per_foot = (0.369 + 0.001472 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "7/8\" High-Temp Foam Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ4-50") {
    if ($frq_mhz <= 10900) {
      $loss_per_foot = (1.0129 + 0.001117 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "1/2\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ5-50") {
	if ($frq_mhz <= 5200) {
      $loss_per_foot = (0.3904 + 0.0006426 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "7/8\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ7-50A") {
    if ($frq_mhz <= 2700) {
      $loss_per_foot = (0.1582 + 0.0004698 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "1-5/8\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ12-50") {
	if ($frq_mhz <= 2300) {
      $loss_per_foot = (0.1222 + 0.0004186 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "2-1/4\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ8-50B") {
    if ($frq_mhz <= 1640) {
      $loss_per_foot = (0.07909 + 0.0004801 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "3\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ11-50") {
    if ($frq_mhz <= 1000) {
      $loss_per_foot = (0.05303 + 0.0004148 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "4\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Andrew HELIAX HJ9-50") {
    if ($frq_mhz <= 960) {
      $loss_per_foot = (0.03655 + 0.0002782 * $frq_mhz) / 100;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "5\" Air Dielectric 50-ohm";
	}
	else {
      $loss_per_foot =  10;
      $loss_per_meter = $loss_per_foot * 3.2808399;
      $cab_desc = "Exceeds Frequency Limit";
    }
  }
  elsif ($val eq "Belden 9913 (RG-8)") {
    $loss_per_foot = ((0.12050 * sqrt $frq_mhz) + (0.00066 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Belden 8237 (RG-8)") {
    $loss_per_foot = ((0.16925 * sqrt $frq_mhz) + (0.00204 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Belden 8267 (RG-213)") {
    $loss_per_foot = ((0.18993 * sqrt $frq_mhz) + (0.00216 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Belden 9258 (RG-8X)") {
    $loss_per_foot = ((0.26904 * sqrt $frq_mhz) + (0.00572 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Belden 8240 (RG-58)") {
    $loss_per_foot = ((0.34190 * sqrt $frq_mhz) + (0.00377 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Crap RG-8") {
    $loss_per_foot = ((0.21 * sqrt $frq_mhz) + (0.00026 * $frq_mhz)) / 100;
    $loss_per_meter = $loss_per_foot * 3.2808399;
  }
  elsif ($val eq "Other") {
    if ($val2 == 0) {
      $val2 = 7; $val1 = "feet";
  }
  if ($val1 eq "meters") {
    $loss_per_meter = $val2 / 100;
    $loss_per_foot = $loss_per_meter / 3.2808399;
   }
   elsif ($val1 eq "feet") {
     $loss_per_foot =  $val2 / 100;
     $loss_per_meter = $loss_per_foot * 3.2808399;
   }
  }
}

## Transmitter Transmission Line
#
&Cable($val = $tx_cab, $val1 = $check1, $val2 = $tx_cab_other);

if ($tx_len_val eq "meters") {
  $tx_cab_desc       = $cab_desc;
  $tx_cab_loss       = sprintf "%.2f", $tx_len * $loss_per_meter;
  $tx_length_m       = sprintf "%.2f", $tx_len;
  $tx_length_ft      = sprintf "%.2f", $tx_len / 0.3048;
  $tx_loss_per_meter = sprintf "%.2f", $loss_per_meter;
  $tx_loss_per_foot  = sprintf "%.2f", $loss_per_foot;
  $tx_loss_per_100m  = sprintf "%.2f", $loss_per_meter * 100;
  $tx_loss_per_100f  = sprintf "%.2f", $loss_per_foot * 100;
}
else {
  $tx_cab_desc       = $cab_desc;
  $tx_cab_loss       = sprintf "%.2f", $tx_len * $loss_per_foot;
  $tx_length_m       = sprintf "%.2f", $tx_len * 0.3048; # ft to m
  $tx_length_ft      = sprintf "%.2f", $tx_len;
  $tx_loss_per_meter = sprintf "%.2f", $loss_per_meter;
  $tx_loss_per_foot  = sprintf "%.2f", $loss_per_foot;
  $tx_loss_per_100m  = sprintf "%.2f", $loss_per_meter * 100;
  $tx_loss_per_100f  = sprintf "%.2f", $loss_per_foot * 100;
}

## Transmitter Transmission Line Efficiency
#
$tx_eff = sprintf "%.f", 100 / (10 ** ($tx_cab_loss / 10)); # percent

if ($tx_eff < 50) {
  $tx_eff_message = "Unacceptable Line Loss";
  $tx_eff_color = "red";
}
else {
  $tx_eff_message = "Acceptable Line Loss";
  $tx_eff_color = "blue";
}

## Transmitter Connector and/or Adapter Loss
#
#$tx_con_loss = $con_tx * 0.025 * $frq_ghz;

## Total Transmitter Transmission Line Loss
#
$tx_total_cable_loss = sprintf "%.2f", $tx_cab_loss + $tx_misc_cab_loss;
$tx_misc_cab_loss    = sprintf "%.2f", $tx_misc_cab_loss;
$tx_misc_loss        = sprintf "%.3f", $tx_misc_loss;
$tx_misc_gain        = sprintf "%.2f", $tx_misc_gain;


## Receiver Transmission Line
#
&Cable($val = $rx_cab, $val1 = $check2, $val2 = $rx_cab_other);

if ($rx_len_val eq "meters") {
  $rx_cab_desc       = $cab_desc;
  $rx_cab_loss       = sprintf "%.2f", $rx_len * $loss_per_meter;
  $rx_length_m       = sprintf "%.2f", $rx_len;
  $rx_length_ft      = sprintf "%.2f", $rx_len / 0.3048; # m to ft
  $rx_loss_per_meter = sprintf "%.2f", $loss_per_meter;
  $rx_loss_per_foot  = sprintf "%.2f", $loss_per_foot;
  $rx_loss_per_100m  = sprintf "%.2f", $loss_per_meter * 100;
  $rx_loss_per_100f  = sprintf "%.2f", $loss_per_foot * 100;
}
else {
  $rx_cab_desc       = $cab_desc;
  $rx_cab_loss       = sprintf "%.2f", $rx_len * $loss_per_foot;
  $rx_length_m       = sprintf "%.2f", $rx_len * 0.3048; # ft to m
  $rx_length_ft      = sprintf "%.2f", $rx_len;
  $rx_loss_per_meter = sprintf "%.2f", $loss_per_meter;
  $rx_loss_per_foot  = sprintf "%.2f", $loss_per_foot;
  $rx_loss_per_100m  = sprintf "%.2f", $loss_per_meter * 100;
  $rx_loss_per_100f  = sprintf "%.2f", $loss_per_foot * 100;
}

## Diversity Antenna Transmission Line Loss
#
if ($do_div eq "yes") {
  if ($rx_div_len_val eq "feet") {
    $rx_div_loss = sprintf "%.2f", ($rx_div_len * $rx_loss_per_foot) + $rx_div_misc_cab_loss;
  }
  elsif ($rx_div_len_val eq "meters") {
    $rx_div_loss = sprintf "%.2f", ($rx_div_len * $rx_loss_per_meter) + $rx_div_misc_cab_loss;
  }
}
elsif ($do_div eq "no")  {
  $rx_div_loss = sprintf "%.2f", 0;
}

$rx_div_misc_cab_loss = sprintf "%.2f", $rx_div_misc_cab_loss;

# Receiver Transmission Line Efficiency
#
$rx_eff = sprintf "%.f", 100 / (10 ** ($rx_cab_loss / 10)); # percent

if ($rx_eff < 50) {
  $rx_eff_message = "Unacceptable Line Loss";
  $rx_eff_color = "red";
}
else {
  $rx_eff_message = "Acceptable Line Loss";
  $rx_eff_color = "blue";
}

## Receiver Connector and/or Adapter Loss
#
#$rx_con_loss = $con_rx * 0.025 * $frq_ghz;

## Total Receiver Transmission Line Loss
#
$rx_total_cable_loss = sprintf "%.2f", $rx_cab_loss + $rx_misc_cab_loss;
$rx_misc_cab_loss    = sprintf "%.2f", $rx_misc_cab_loss;
$rx_misc_gain       = sprintf "%.2f", $rx_misc_gain;

## Calculate rain absorption
#
$rate =~ tr/0-9.//csd;

if ($rain eq "A: Polar Tundra") {
  $rate = sprintf "%.1f", 15.0;
  $region = "A: Polar Tundra";
}
elsif ($rain eq "B: Polar Taiga - Moderate") {
  $rate = sprintf "%.1f", 19.0;
  $region = "B: Polar Taiga - Moderate";
}
elsif ($rain eq "C: Temperate Maritime") {
  $rate = sprintf "%.1f", 28.0;
  $region = "C: Temperate Maritime";
}
elsif ($rain eq "D1: Temperate Continental - Dry") {
  $rate = sprintf "%.1f", 37.0;
  $region = "D1: Temperate Continental - Dry";
}
elsif ($rain eq "D2: Temperate Continental - Mid") {
  $rate = sprintf "%.1f", 49.0;
  $region = "D2: Temperate Continental - Mid";
}
elsif ($rain eq "D3: Temperate Continental - Wet") {
  $rate = sprintf "%.1f", 63.0;
  $region = "D3: Temperate Continental - Wet";
}
elsif ($rain eq "E: Subtropical - Wet") {
  $rate = sprintf "%.1f", 98.0;
  $region = "E: Subtropical - Wet";
}
elsif ($rain eq "F: Subtropical - Arid") {
  $rate = sprintf "%.1f", 23.0;
  $region = "F: Subtropical - Arid";
}
elsif ($rain eq "G: Tropical - Moderate") {
  $rate = sprintf "%.1f", 67.0;
  $region = "G: Tropical - Moderate";
}
elsif ($rain eq "H: Tropical - Wet") {
  $rate = sprintf "%.1f", 147.0;
  $region = "H: Tropical - Wet";
}
elsif ($rain eq "None") {
   $rate = sprintf "%.1f", $rate;
   $region = "User Supplied";

   if ($rate > 200) {
     $rate = 200;
   }
}

## Effective Rain Distance, ITU P.530
#
$rain_eff_km = sprintf "%.2f", (1 / (1 + ($dist_km / (35 * exp(-0.015 * $rate))))) * $dist_km;
$rain_eff_mi = sprintf "%.2f", $rain_eff_km / 1.609344;
 
## NASA Simplified Rain Attenuation
#
if ($frq_ghz >= 2.0 && $frq_ghz <= 54) {
  $nasa_a = (4.21 * (10 ** -5)) * ($frq_ghz ** 2.42);
}
elsif ($frq_ghz > 54 && $frq_ghz <= 180)  {
  $nasa_a = (4.09 * (10 ** -2)) * ($frq_ghz ** 0.669);
}
else {
  $nasa_a = 0;
}

if ($frq_ghz >= 2.0 && $frq_ghz <= 25) {
  $nasa_b = 1.41 * ($frq_ghz ** -0.0779);
}
elsif ($frq_ghz > 25 && $frq_ghz <= 164) {
  $nasa_b = 2.63 * ($frq_ghz ** -0.272);
}
else {
  $nasa_b = 0;
}

$nasa_rain_att_total = sprintf "%.3f", ($nasa_a * ($rate ** $nasa_b)) * $rain_eff_km;

## Crane Rain Attenuation Model
#
if ($frq_mhz >= 500 && $frq_mhz < 2000) {
  if ($polar eq "Vertical") {
    $Kv_y1 = 0.0000352; $Av_y1 = 0.880;
	$Kv_y2 = 0.0001380; $Av_y2 = 0.923;
    $A = $Av_y1 + (($frq_mhz - 1000) / (2000 - 1000)) * ($Av_y2 - $Av_y1);
	$K = 10 ** (log10($Kv_y1) + (($frq_mhz - 1000) / (2000 - 1000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0000387; $Ah_y1 = 0.912;
    $Kh_y2 = 0.0001540; $Ah_y2 = 0.963;
    $A = $Ah_y1 + (($frq_mhz - 1000) / (2000 - 1000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 1000) / (2000 - 1000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 2000 && $frq_mhz < 4000) {
  if ($polar eq "Vertical") {
    $Kv_y1 = 0.0001380; $Av_y1 = 0.923;
    $Kv_y2 = 0.0005910; $Av_y2 = 1.075;
	$A = $Av_y1 + (($frq_mhz - 2000) / (4000 - 2000)) * ($Av_y2 - $Av_y1);
	$K = 10 ** (log10($Kv_y1) + (($frq_mhz - 2000) / (4000 - 2000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0001540; $Ah_y1 = 0.963;
    $Kh_y2 = 0.0006500; $Ah_y2 = 1.121;
	$A = $Ah_y1 + (($frq_mhz - 2000) / (4000 - 2000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 2000) / (4000 - 2000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 4000  && $frq_mhz < 6000) {
  if ($polar eq "Vertical") {
    $Kv_y1 = 0.0005910; $Av_y1 = 1.075;
    $Kv_y2 = 0.0015500; $Av_y2 = 1.265;
    $A = $Av_y1 + (($frq_mhz - 4000) / (6000 - 4000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 4000) / (6000 - 4000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0006500; $Ah_y1 = 1.121;
    $Kh_y2 = 0.0017500; $Ah_y2 = 1.308;
    $A = $Ah_y1 + (($frq_mhz - 4000) / (6000 - 4000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 4000) / (6000 - 4000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 6000  && $frq_mhz < 7000) {
  if ($polar eq "Vertical") {
    $Kv_y1 = 0.0015500; $Av_y1 = 1.265;
    $Kv_y2 = 0.0026500; $Av_y2 = 1.012;
    $A = $Av_y1 + (($frq_mhz - 6000) / (7000 - 6000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 6000) / (7000 - 6000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0017500; $Ah_y1 = 1.308;
    $Kh_y2 = 0.0030100; $Ah_y2 = 1.332;
    $A = $Ah_y1 + (($frq_mhz - 6000) / (7000 - 6000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 6000) / (7000 - 6000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 7000  && $frq_mhz < 8000) {
  if ($polar eq "Vertical") { 
    $Kv_y1 = 0.0026500; $Av_y1 = 1.012;
    $Kv_y2 = 0.0039500; $Av_y2 = 1.310;
    $A = $Av_y1 + (($frq_mhz - 7000) / (8000 - 7000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 7000) / (8000 - 7000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0030100; $Ah_y1 = 1.332;
    $Kh_y2 = 0.0045400; $Ah_y2 = 1.327;
    $A = $Ah_y1 + (($frq_mhz - 7000) / (8000 - 7000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 7000) / (8000 - 7000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 8000  && $frq_mhz < 10000) {
  if ($polar eq "Vertical") { 
    $Kv_y1 = 0.0039500; $Av_y1 = 1.310;
    $Kv_y2 = 0.0088700; $Av_y2 = 1.264;
    $A = $Av_y1 + (($frq_mhz - 8000) / (10000 - 8000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 7000) / (8000 - 7000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0045400; $Ah_y1 = 1.327;
    $Kh_y2 = 0.0101000; $Ah_y2 = 1.276;
    $A = $Ah_y1 + (($frq_mhz - 8000) / (10000 - 8000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 8000) / (10000 - 8000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 10000  && $frq_mhz < 12000) {
  if ($polar eq "Vertical") { 
    $Kv_y1 = 0.0088700; $Av_y1 = 1.264;
    $Kv_y2 = 0.0168000; $Av_y2 = 1.200;
    $A = $Av_y1 + (($frq_mhz - 10000) / (12000 - 10000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 10000) / (12000 - 10000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0101000; $Ah_y1 = 1.276;
    $Kh_y2 = 0.0188000; $Ah_y2 = 1.217;
    $A = $Ah_y1 + (($frq_mhz - 10000) / (12000 - 10000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 10000) / (12000 - 10000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 12000  && $frq_mhz < 15000) {
  if ($polar eq "Vertical") { 
    $Kv_y1 = 0.0168000; $Av_y1 = 1.200;
    $Kv_y2 = 0.0335000; $Av_y2 = 1.128;
    $A = $Av_y1 + (($frq_mhz - 12000) / (15000 - 12000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 12000) / (15000 - 12000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0188000; $Ah_y1 = 1.217;
    $Kh_y2 = 0.0367000; $Ah_y2 = 1.154;
    $A = $Ah_y1 + (($frq_mhz - 12000) / (15000 - 12000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 12000) / (15000 - 12000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 15000  && $frq_mhz < 20000) {
  if ($polar eq "Vertical") { 
    $Kv_y1 = 0.0335000; $Av_y1 = 1.128;
    $Kv_y2 = 0.0691000; $Av_y2 = 1.065;
    $A = $Av_y1 + (($frq_mhz - 15000) / (20000 - 15000)) * ($Av_y2 - $Av_y1);
    $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 15000) / (20000 - 15000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0367000; $Ah_y1 = 1.154;
    $Kh_y2 = 0.0751000; $Ah_y2 = 1.099;
    $A = $Ah_y1 + (($frq_mhz - 15000) / (20000 - 15000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 15000) / (20000 - 15000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
elsif ($frq_mhz >= 20000  && $frq_mhz < 25000) {
  if ($polar eq "Vertical") { 
   $Kv_y1 = 0.0691000; $Av_y1 = 1.065;
   $Kv_y2 = 0.1130000; $Av_y2 = 1.030;
   $A = $Av_y1 + (($frq_mhz - 20000) / (25000 - 20000)) * ($Av_y2 - $Av_y1);
   $K = 10 ** (log10($Kv_y1) + (($frq_mhz - 20000) / (25000 - 20000)) * (log10($Kv_y2) - log10($Kv_y1)));
  }
  elsif ($polar eq "Horizontal") {
    $Kh_y1 = 0.0751000; $Ah_y1 = 1.099;
    $Kh_y2 = 0.1240000; $Ah_y2 = 1.061;
    $A = $Ah_y1 + (($frq_mhz - 20000) / (25000 - 20000)) * ($Ah_y2 - $Ah_y1);
    $K = 10 ** (log10($Kh_y1) + (($frq_mhz - 20000) / (25000 - 20000)) * (log10($Kh_y2) - log10($Kh_y1)));
  }
}
else {
  $A = 0;
  $K = 0;
}

$Do = 3.8 - (0.6 * log($rate));
$B  = 2.3 * ($rate ** -0.17);
$c  = 0.026 - (0.03 * log($rate));
$u  = (log($B * exp($c * $Do))) / $Do;

if ((0 <= $dist_km) && ($dist_km <= $Do)) {
  $VAR_A = ((exp($u * $A * $dist_km) - 1) / ($u * $A));
  $Ar = ($K * ($rate ** $A)) * $VAR_A;              

  $crane_rain_att_mi    = sprintf "%.3f", $Ar / $dist_mi;
  $crane_rain_att_km    = sprintf "%.3f", $Ar / $dist_km;
  $crane_rain_att_total = sprintf "%.3f", $crane_rain_att_km * $rain_eff_km;
}
elsif (($Do <= $dist_km) && ($dist_km <= 22.5)) {
  $VAR_A = ((exp($u * $A * $Do) - 1) / ($u * $A));
  $VAR_B = ((($B ** $A) * exp($c * $A * $Do)) / ($c * $A));
  $VAR_C = ((($B ** $A) * exp($c * $A * $dist_km)) / ($c * $A));
  $Ar = ($K * ($rate ** $A)) * (($VAR_A - $VAR_B) + $VAR_C);

  $crane_rain_att_mi    = sprintf "%.3f", $Ar / $dist_mi;
  $crane_rain_att_km    = sprintf "%.3f", $Ar / $dist_km;
  $crane_rain_att_total = sprintf "%.3f", $crane_rain_att_km * $rain_eff_km;
}
elsif ($dist_km > 22.5) {
  $VAR_A = ((exp($u * $A * $Do) - 1) / ($u * $A));
  $VAR_B = ((($B ** $A) * exp($c * $A * $Do)) / ($c * $A));
  $VAR_C = ((($B ** $A) * exp($c * $A * 22.5)) / ($c * $A));
  $Ar = ($K * ($rate ** $A)) * (($VAR_A - $VAR_B) + $VAR_C);

  $crane_rain_att_mi    = sprintf "%.3f", ($Ar * ($dist_km / 22.5)) / $dist_mi;
  $crane_rain_att_km    = sprintf "%.3f", ($Ar * ($dist_km / 22.5)) / $dist_km;
  $crane_rain_att_total = sprintf "%.3f", $crane_rain_att_km * $rain_eff_km;
}

## Atmospheric Attenuation (oxygen loss)
#
# ITU-R P.676-3
$rt = 288.15 / (273.15 + $temp_c);
$rp = $atmos_p / 1013.25;

if ($frq_ghz <= 57) {
  # Below 57 GHz
  $oxya = (7.27 * $rt) / ((($frq_ghz ** 2) + 0.351) * ($rp ** 2) * ($rt ** 2));
  $oxyb = 7.50 / (((abs($frq_ghz - 57) ** 2) + 2.44) * ($rp ** 2) * ($rt ** 5));
  $oxy_att_km = ($oxya + $oxyb) * ($frq_ghz ** 2) * ($rp ** 2) * ($rt ** 2) * (10 ** -3);
  $oxy_att_mi    = $oxy_att_km / 1.609344;
  $oxy_att_total = sprintf "%.3f", $oxy_att_mi * $dist_mi;
  $oxy_att_mi    = sprintf "%.4f", $oxy_att_mi;
  $oxy_att_km    = sprintf "%.4f", $oxy_att_km;

}
elsif (57 < $frq_ghz && $frq_ghz <= 63) {
  # Between 57 and 63 GHz
  $oxy_att_km    = 14.9;  # 14.9 dB per km at 60 GHz
  $oxy_att_mi    = $oxy_att_km / 1.609344;
  $oxy_att_total = sprintf "%.3f", $oxy_att_mi * $dist_mi;
  $oxy_att_mi    = sprintf "%.4f", $oxy_att_mi;
  $oxy_att_km    = sprintf "%.4f", $oxy_att_km;
}
elsif (63 <= $frq_ghz && $frq_ghz <= 350) {
  # Above 63 GHz
  $oxya = (2 * (10 ** -4)) * ($rt ** 1.5) * (1 - ((1.2 * (10 ** -5)) * ($frq_ghz ** 1.5)));
  $oxyb = 4 / (((abs($frq_ghz - 63) ** 2) + 1.5) * ($rp ** 2) * ($rt ** 5));
  $oxyc = (0.28 * ($rt ** 2)) / (((($frq_ghz - 118.75) ** 2) + 2.84) * ($rp ** 2) * ($rt ** 2));
  $oxy_att_km = ($oxya + $oxyb + $oxyc) * ($frq_ghz ** 2) * ($rp ** 2) * ($rt ** 2) * (10 ** -3);
  $oxy_att_mi = $oxy_att_km / 1.609344;
  $oxy_att_total = sprintf "%.3f", $oxy_att_mi * $dist_mi;
  $oxy_att_mi    = sprintf "%.4f", $oxy_att_mi;
  $oxy_att_km    = sprintf "%.4f", $oxy_att_km;
}

## Water Vapor Attenuation
#
$wvd =~ tr/0-9.//csd;

if (!$wvd || $wvd == 0.0) {
  $wvd = sprintf "%.2f", 7.5; # water vapor density in gram/meter-cubed, 7.5 corresponds to 50% humidity @ 16C or 75% humidity at 10C
}

if ($frq_ghz <= 350) {
  # ITU-R P.676-3
  $wvpa = 0.0327 * $rt;
  $wvpb = 0.00167 * (($wvd * ($rt ** 7)) / $rp);
  $wvpc = 0.00077 * ($frq_ghz ** 0.5);
  $wvpd = 3.79 / ((($frq_ghz - 22.235) ** 2) + 9.81 * ($rp ** 2) * $rt);
  $wvpe = 11.73 * $rt / ((($frq_ghz - 183.31) ** 2) + 11.85 * ($rp ** 2) * $rt);
  $wvpf = 4.01 * $rt / ((($frq_ghz - 325.153) ** 2) + 10.44 * ($rp ** 2) * $rt);

  $water_att_km    = ($wvpa + $wvpb + $wvpc + $wvpd + $wvpe + $wvpf) * ($frq_ghz ** 2) * $wvd * $rp * $rt * 0.0001;
  $water_att_mi    = $water_att_km / 1.609344;
  $water_att_total = sprintf "%.3f", $water_att_mi * $dist_mi;
  $water_att_mi    = sprintf "%.4f", $water_att_mi;
  $water_att_km    = sprintf "%.4f", $water_att_km;
}

## Fog Attenuation - NASA / 10-100 GHz 
#
if ($frq_ghz >= 5.0) {
  # Fog density, dB/km/g/m3
  $af = -1.347 + (11.152 / $frq_ghz) + (0.060 * $frq_ghz) - (0.022 * $temp_c);
  # Fog density for km visibility, g/m3
  $vis = 0.1; # visibility in km
  $M = (0.024 / $vis) ** 1.54; 
  # Total fog attenation, use same as effective rain distance
  $extent = $rain_eff_mi;
  $AF = $af * $M * $extent;
  $fog_att = sprintf "%.3f", $AF;
  $fvis = sprintf "%.f", $vis * 3280.8399;
  #$fdis = sprintf "%.f", $extent / 1.609344;
  $fog_message = "(Visibility: <font color=\"blue\">$fvis</font> ft / Coverage: <font color=\"blue\">$rain_eff_mi</font> mi)";
}
elsif ($frq_ghz < 5.0) {
  $fog_att = sprintf "%.3f", 0;
  $fog_message = "";
}

# Total Atmospheric Attenuation
#
$atmos_norain = sprintf "%.2f", $oxy_att_total + $water_att_total;
$atmos_rain   = sprintf "%.2f", $oxy_att_total + $water_att_total + $crane_rain_att_total;

## Effective Isotropic Radiated Power (EIRP)
#
$eirp     = sprintf "%.2f", ($pwr_out_dbm - $tx_total_cable_loss) + $tx_misc_gain + $tx_ant_gain_dbi;
$eirp_mw  = sprintf "%.2f", 10 ** ($eirp / 10);
$eirp_w   = sprintf "%.2f", 10 ** (($eirp - 30) / 10);
$eirp_dbw = sprintf "%.2f", 10 * log10((10 ** (($eirp - 30) / 10)));
$eirp_kw  = sprintf "%.2f", (10 ** (($eirp - 30) / 10)) / 1000;
$eirp_dbk = sprintf "%.2f", (10 * log10((10 ** (($eirp - 30) / 10)))) - 30;

## RF Input to the Antenna
#
$tx_ant_input_mw = sprintf "%.2f", 10 ** ((($pwr_out_dbm - $tx_total_cable_loss) + $tx_misc_gain) / 10);
$tx_ant_input    = sprintf "%.2f", ($pwr_out_dbm - $tx_total_cable_loss) + $tx_misc_gain;

## RF Input Power, FCC Part 15.247
#
if ($tx_ant_gain_dbi == 0 || $tx_ant_gain_dbi <= 6) {
  $max_ant_pwr    = sprintf "%.2f", 30;
  $max_ant_pwr_mw = sprintf "%.2f", 10 ** (30 / 10);
}

if ($tx_ant_gain_dbi > 6) {
  $max_ant_pwr    = sprintf "%.2f", 30 - (($tx_ant_gain_dbi - 6) / 3);
  $max_ant_pwr_mw = sprintf "%.2f", 10 ** ($max_ant_pwr / 10);
}

# FCC Part 74.644/74.636 Max EIRP Check
#
# https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-74/subpart-F/section-74.636
if ($frq_mhz >= 2025 && $frq_mhz <= 2110) {
  $MAXEIRP = 45; # dBW
}
elsif ($frq_mhz >= 2450 && $frq_mhz <= 2484) {
  $MAXEIRP = 45; # dBW
}
elsif ($frq_mhz >= 6875 && $frq_mhz <= 7125) {
  $MAXEIRP = 55; # dBW
}
elsif ($frq_mhz >= 12700 && $frq_mhz <= 13250) {
  $MAXEIRP = 55; # dBW
}
elsif ($frq_mhz >= 17700 && $frq_mhz < 18600) {
  $MAXEIRP = 55; # dBW
}
elsif ($frq_mhz >= 18600 && $frq_mhz <= 18800) {
  $MAXEIRP = 35; # dBW
}
elsif ($frq_mhz > 18800 && $frq_mhz <= 19700) {
  $MAXEIRP = 55; # dBW
}
else {
  $MAXEIRP = "N/A";
}

if ($frq_mhz >= 1990 && $frq_mhz <= 7125) {
  $path_min = 17; # Minimum path length in kilometers
}
elsif ($frq_mhz >= 12200 && $frq_mhz <= 13250) {
  $path_min = 5; # Minimum path length in kilometers
}
else {
  $path_min = "N/A";
}

if ($path_min eq "N/A") {
  if ($MAXEIRP eq "N/A") {
    $fcc_eirp_dbm = "N/A";
    $fcc_eirp_mw = "N/A";
  }
  else {
    $fcc_eirp_dbm = sprintf "%.2f", $MAXEIRP + 30; # dBW to dBm
	$fcc_eirp_mw  = sprintf "%.2f", 10 ** (($MAXEIRP + 30) / 10); # dBm to mW

	if ($eirp <= $fcc_eirp_dbm) {
	  $fcc_check = "(EIRP Pass)";
	}
	elsif ($eirp > $fcc_eirp_dbm) {
      $fcc_check = "(EIRP Fail)";
	}
  }
}
elsif ($path_min > 0) {
  if ($MAXEIRP eq "N/A") {
    $fcc_eirp_dbm = "N/A";
    $fcc_eirp_mw = "N/A";
  }
  else {
    $fcc_eirp = 30 - 20 * log10($path_min / $dist_km);
    $fcc_eirp_dbm = sprintf "%.2f", $fcc_eirp + 30;
    $fcc_eirp_mw  = sprintf "%.2f",  10 ** ($fcc_eirp / 10);

    if ($eirp <= $fcc_eirp_dbm) {
      $fcc_check = "(EIRP Pass)";
    }
    elsif ($eirp > $fcc_eirp_dbm) {
      $fcc_check = "(EIRP Fail)";
    }
  }
}

## Calculate Free-Space and ITM Losses
#
$fs      = sprintf "%.2f", (20 * (log10 $frq_mhz)) + (20 * (log10 $dist_km)) + 32.447782;
$fs_rain = sprintf "%.2f", ((20 * (log10 $frq_mhz)) + (20 * (log10 $dist_km)) + 32.447782) + $crane_rain_att_total;
$itm_rain = sprintf "%.2f", $itm + $crane_rain_att_total;

# Total Free-Space Path Loss = Free-Space + Atmospheric Losses + Misc.
$fs_pl      = sprintf "%.2f", $fs + $atmos_norain + $tx_misc_loss;
$fs_pl_rain = sprintf "%.2f", $fs + $atmos_rain + $tx_misc_loss;

# Total ITM Path Loss = ITM + Atmospheric Losses + Misc
if ($do_div eq "no") {
  $itm_pl          = sprintf "%.2f", $itm + $atmos_norain + $tx_misc_loss;
  $itm_pl_rain     = sprintf "%.2f", $itm + $atmos_rain + $tx_misc_loss;
  $div_itm_pl      = sprintf "%.2f", 0;
  $div_itm_pl_rain = sprintf "%.2f", 0;
}
elsif ($do_div eq "yes") {
  $itm_pl          = sprintf "%.2f", $itm + $atmos_norain + $tx_misc_loss;
  $itm_pl_rain     = sprintf "%.2f", $itm + $atmos_rain + $tx_misc_loss;
  $div_itm_pl      = sprintf "%.2f", $div_itm + $atmos_norain + $tx_misc_loss;
  $div_itm_pl_rain = sprintf "%.2f", $div_itm + $atmos_rain + $tx_misc_loss;
}

## Received Power Level - Free-Space
#
$rx_pwr       = sprintf "%.2f", ($eirp - $fs_pl) + (($rx_ant_gain_dbi + $rx_misc_gain) - $rx_total_cable_loss);
$rx_pwr_uvolt = sprintf "%.2f", (sqrt(( 10 ** ($rx_pwr / 10) / 1000) * 50)) * 1000000;

$rx_pwr_rain       = sprintf "%.2f", ($eirp - $fs_pl_rain) + (($rx_ant_gain_dbi + $rx_misc_gain) - $rx_total_cable_loss);
$rx_pwr_rain_uvolt = sprintf "%.2f", (sqrt(( 10 ** ($rx_pwr_rain / 10) / 1000) * 50)) * 1000000;

$rx_div_pwr        = sprintf "%.2f", ($eirp - $fs_pl) + (($div_ant_dbi + $rx_misc_gain) - $rx_div_loss);
$rx_div_pwr_rain   = sprintf "%.2f", ($eirp - $fs_pl_rain) + (($div_ant_dbi + $rx_misc_gain) - $rx_div_loss);

## Received Power Level - ITM
#
$rx_pwr_itm       = sprintf "%.2f", ($eirp - $itm_pl) + (($rx_ant_gain_dbi + $rx_misc_gain) - $rx_total_cable_loss);
$rx_pwr_itm_uvolt = sprintf "%.2f", (sqrt(( 10 ** ($rx_pwr_itm / 10) / 1000) * 50)) * 1000000;

$rx_pwr_itm_rain       = sprintf "%.2f", ($eirp - $itm_pl_rain) + (($rx_ant_gain_dbi + $rx_misc_gain) - $rx_total_cable_loss);
$rx_pwr_itm_rain_uvolt = sprintf "%.2f", (sqrt(( 10 ** ($rx_pwr_itm_rain / 10) / 1000) * 50)) * 1000000;

if ($do_div eq "yes") {
  $rx_div_pwr_itm       = sprintf "%.2f", ($eirp - $div_itm_pl) + (($div_ant_dbi + $rx_misc_gain) - $rx_div_loss);
  $rx_div_pwr_itm_rain  = sprintf "%.2f", ($eirp - $div_itm_pl_rain) + (($div_ant_dbi + $rx_misc_gain) - $rx_div_loss);

  $rx_div_pwr_itm_uvolt      = sprintf "%.2f", (sqrt(( 10 ** ($rx_div_pwr_itm / 10) / 1000) * 50)) * 1000000;
  $rx_div_pwr_itm_rain_uvolt = sprintf "%.2f", (sqrt(( 10 ** ($rx_div_pwr_itm_rain / 10) / 1000) * 50)) * 1000000;

}
elsif ($do_div eq "no") {
  $rx_div_pwr_itm            = "Not Applicable";
  $rx_div_pwr_itm_rain       = "Not Applicable";
  $rx_div_pwr_itm_uvolt      = "N/A";
  $rx_div_pwr_itm_rain_uvolt = "N/A";
}

## Receiver Threshold
#
$BER =~ tr/0-9.-//csd;
$BER_crit =~ tr/A-Za-z0-9.\-\ //csd;

$BER_dbm   = sprintf "%.2f", $BER; # dBm
$BER_uvolt = sprintf "%.2f", (sqrt((10 ** ($BER / 10) / 1000) * 50)) * 1000000; # dBm to uV

## Thermal Fade Margin - Free-Space
#
if ($rx_pwr >= $BER_dbm) {
  $tfm = sprintf "%.2f", abs($BER_dbm - $rx_pwr);
}
else {
  $tfm = sprintf "%.2f", abs($BER_dbm - $rx_pwr) * -1;
}

if ($rx_pwr_rain >= $BER_dbm) {
  $tfm_rain = sprintf "%.2f", abs($BER_dbm - $rx_pwr_rain);
}
else {
  $tfm_rain = sprintf "%.2f", abs($BER_dbm - $rx_pwr_rain) * -1;
}

if ($tfm <= 0) {
  $tfm_color = "red";
}
else {
  $tfm_color = "blue";
}

if ($tfm_rain <= 0) {
  $tfm_color_rain = "red";
}
else {
  $tfm_color_rain = "blue";
}

if ($do_div eq "yes") {
  if ($rx_div_pwr >= $BER_dbm) {
    $div_tfm = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr);
  }
  else {
    $div_tfm = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr) * -1;
  }

  if ($rx_div_pwr_rain >= $BER_dbm) {
    $div_tfm_rain = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr_rain);
  }
  else {
    $div_tfm_rain = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr_rain) * -1;
  }

  if ($div_tfm <= 0) {
    $div_tfm_color = "red";
  }
  else {
    $div_tfm_color = "blue";
  }

  if ($div_tfm_rain <= 0) {
    $div_tfm_color_rain = "red";
  }
  else {
    $div_tfm_color_rain = "blue";
  }

}
else {
  $div_tfm = sprintf "%.2f", 0;
  $div_tfm_rain = sprintf "%.2f", 0;
}

## Thermal Fade Margin - ITM
#
if ($rx_pwr_itm >= $BER_dbm) {
  $tfm_itm = sprintf "%.2f", abs($BER_dbm - $rx_pwr_itm);
 }
else {
  $tfm_itm = sprintf "%.2f", ($BER_dbm - $rx_pwr_itm) * -1;
}

if ($rx_pwr_itm_rain >= $BER_dbm) {
  $tfm_itm_rain = sprintf "%.2f", abs($BER_dbm - $rx_pwr_itm_rain);
}
else {
  $tfm_itm_rain = sprintf "%.2f", ($BER_dbm - $rx_pwr_itm_rain) * -1;
}

if ($tfm_itm <= 0) {
  $tfm_itm_color = "red";
}
else {
  $tfm_itm_color = "blue";
}

if ($tfm_itm_rain <= 0) {
  $tfm_itm_color_rain = "red";
}
else {
  $tfm_itm_color_rain = "blue";
}


if ($do_div eq "yes") {
  if ($rx_div_pwr_itm >= $BER_dbm) {
    $div_tfm_itm = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr_itm);
  }
  else {
    $div_tfm_itm = sprintf "%.2f", ($BER_dbm - $rx_div_pwr_itm) * -1;
  }

  if ($rx_div_pwr_itm_rain >= $BER_dbm) {
    $div_tfm_itm_rain = sprintf "%.2f", abs($BER_dbm - $rx_div_pwr_itm_rain);
  }
  else {
    $div_tfm_itm_rain = sprintf "%.2f", ($BER_dbm - $rx_div_pwr_itm_rain) * -1;
  }
}
else {
  $div_tfm_itm        = "Not Applicable";
  $div_tfm_itm_rain   = "Not Applicable";
  $div_tfm_color      = "blue";
  $div_tfm_color_rain = "blue";
}

## Vigants Composite, Dispersive, External Interference, Adjacent Channel Fade Margins - Free-Space and ITM
# 
$dfm  =~ tr/0-9.//csd;
$eifm =~ tr/0-9.//csd;
$aifm =~ tr/0-9.//csd;

if ($dfm == 0) {

  $cmp_fs       = sprintf "%.2f", $tfm;
  $cmp_fs_rain  = sprintf "%.2f", $tfm_rain;
  $cmp_itm      = sprintf "%.2f", $tfm_itm;
  $cmp_itm_rain = sprintf "%.2f", $tfm_itm_rain;
  $eifm_fs      = sprintf "%.2f", $eifm;
  $aifm_fs      = sprintf "%.2f", $aifm;
  $dfm_fs = $comp_fs = sprintf "%.2f", 0;

  if ($do_div eq "no") {
    $cmp_div_itm = "Not Applicable";
	$cmp_div_itm_color = "blue";
	$cmp_div_itm_rain = "Not Applicable";
	$cmp_div_itm_rain_color = "blue";
  }
  elsif ($do_div eq "yes") {
    $cmp_div_itm = sprintf "%.2f", $div_tfm_itm;
    $cmp_div_itm_rain = sprintf "%.2f", $div_tfm_itm_rain; 
    
	if ($cmp_div_itm < 0) {
	  $cmp_div_itm_color = "red";
	}
	elsif ($cmp_div_itm > 0) {
	  $cmp_div_itm_color = "blue";
	}

   if ($cmp_div_itm_rain < 0) {
      $cmp_div_itm_rain_color = "red";
    }
    elsif ($cmp_div_itm_rain > 0) {
      $cmp_div_itm_rain_color = "blue";
    }

  }

  if ($cmp_itm < 0) {
    $cmp_itm_color = "red";
  }
  elsif ($cmp_itm > 0) {
    $cmp_itm_color = "blue";
  }

  if ($cmp_itm_rain < 0) {
    $cmp_itm_rain_color = "red";
  }
  elsif ($cmp_itm_rain > 0) {
    $cmp_itm_rain_color = "blue";
  }

  if ($cmp_fs < 0) {
    $cmp_fs_color = "red";
  }
  elsif ($cmp_fs > 0) {
    $cmp_fs_color = "blue";
  }

  if ($cmp_fs_rain < 0) {
    $cmp_fs_rain_color = "red";
  }
  elsif ($cmp_fs_rain > 0) {
    $cmp_fs_rain_color = "blue";
  }
}
elsif ($dfm && ($eifm == 0) && ($aifm == 0)) {
  $comp          = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm / 10))));
  $comp_rain     = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_rain / 10))));
  $comp_itm      = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_itm / 10))));
  $comp_itm_rain = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_itm_rain / 10)))); 

  $comp_fs      = sprintf "%.2f", $comp;
  $cmp_fs       = sprintf "%.2f", $comp;
  $cmp_fs_rain  = sprintf "%.2f", $comp_rain;
  $cmp_itm      = sprintf "%.2f", $comp_itm;
  $cmp_itm_rain = sprintf "%.2f", $comp_itm_rain;
  $comp_itm     = sprintf "%.2f", $comp_itm;
  $dfm_fs       = sprintf "%.2f", $dfm;
  $eifm_fs      = sprintf "%.2f", 0;
  $aifm_fs      = sprintf "%.2f", 0;

  if ($do_div eq "no") {
    $cmp_div_itm = "Not Applicable";
	$cmp_div_itm_color = "blue";
    $cmp_div_itm_rain = "Not Applicable";
    $cmp_div_itm_rain_color = "blue";
  }
  elsif ($do_div eq "yes") {
    $cmp_div_itm = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm / 10))));
    $cmp_div_itm_rain = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm_rain / 10))))

  }

   if ($cmp_itm < 0) {
    $cmp_itm_color = "red";
  }
  elsif ($cmp_itm > 0) {
    $cmp_itm_color = "blue";
  }

  if ($cmp_itm_rain < 0) {
    $cmp_itm_rain_color = "red";
  }
  elsif ($cmp_itm_rain > 0) {
    $cmp_itm_rain_color = "blue";
  }

  if ($cmp_fs < 0) {
    $cmp_fs_color = "red";
  }
  elsif ($cmp_fs > 0) {
    $cmp_fs_color = "blue";
  }

  if ($cmp_fs_rain < 0) {
   $cmp_fs_rain_color = "red";
  }
  elsif ($cmp_fs_rain > 0) {
    $cmp_fs_rain_color = "blue";
  }

}
elsif ($dfm && $eifm && ($aifm == 0)) {
  $comp        = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm / 10))) + ((10 ** (-$eifm / 10))));
  $comp_itm    = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_itm / 10))) + ((10 ** (-$eifm / 10))));
  $cmp_fs      = sprintf "%.2f", $comp;
  $comp_fs     = sprintf "%.2f", $comp;
  $cmp_itm     = sprintf "%.2f", $comp_itm;
  $comp_itm    = sprintf "%.2f", $comp_itm;
  $dfm_fs      = sprintf "%.2f", $dfm;
  $eifm_fs     = sprintf "%.2f", $eifm;
  $aifm_fs     = sprintf "%.2f", 0;

  if ($do_div eq "no") {
    $cmp_div_itm = "Not Applicable";
	$cmp_div_itm_color = "blue";
    $cmp_div_itm_rain = "Not Applicable";
    $cmp_div_itm_rain_color = "blue";
  }
  elsif ($do_div eq "yes") {
    $cmp_div_itm = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm / 10))) + ((10 ** (-$eifm / 10))));
    $cmp_div_itm_rain = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm_rain / 10))) + ((10 ** (-$eifm / 10))));


  }

   if ($cmp_itm < 0) {
    $cmp_itm_color = "red";
  }
  elsif ($cmp_itm > 0) {
    $cmp_itm_color = "blue";
  }

  if ($cmp_itm_rain < 0) {
    $cmp_itm_rain_color = "red";
  }
  elsif ($cmp_itm_rain > 0) {
    $cmp_itm_rain_color = "blue";
  }

  if ($cmp_fs < 0) {
    $cmp_fs_color = "red";
  }
  elsif ($cmp_fs > 0) {
    $cmp_fs_color = "blue";
  }

  if ($cmp_fs_rain < 0) {
    $cmp_fs_rain_color = "red";
  }
  elsif ($cmp_fs_rain > 0) {
    $cmp_fs_rain_color = "blue";
  }

}
elsif ($dfm && $aifm && ($eifm == 0)) {
  $comp        = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm / 10))) + ((10 ** (-$aifm / 10))));
  $comp_itm    = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_itm / 10))) + ((10 ** (-$aifm / 10))));
  $cmp_fs      = sprintf "%.2f", $comp;
  $comp_fs     = sprintf "%.2f", $comp;
  $cmp_itm     = sprintf "%.2f", $comp_itm;
  $comp_fs_itm = sprintf "%.2f", $comp_itm;
  $dfm_fs      = sprintf "%.2f", $dfm;
  $aifm_fs     = sprintf "%.2f", $aifm;
  $eifm_fs     = sprintf "%.2f", 0;

  if ($do_div eq "no") {
    $cmp_div_itm = "Not Applicable";
	$cmp_div_itm_color = "blue";
    $cmp_div_itm_rain = "Not Applicable";
    $cmp_div_itm_rain_color = "blue";
  }
  elsif ($do_div eq "yes") {
    $cmp_div_itm = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm / 10))) + ((10 ** (-$aifm / 10))));
    $cmp_div_itm_rain = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm_rain / 10))) + ((10 ** (-$aifm / 10))));

  }

   if ($cmp_itm < 0) {
    $cmp_itm_color = "red";
  }
  elsif ($cmp_itm > 0) {
    $cmp_itm_color = "blue";
  }

  if ($cmp_itm_rain < 0) {
    $cmp_itm_rain_color = "red";
  }
  elsif ($cmp_itm_rain > 0) {
    $cmp_itm_rain_color = "blue";
  }

  if ($cmp_fs < 0) {
    $cmp_fs_color = "red";
  }
  elsif ($cmp_fs > 0) {
    $cmp_fs_color = "blue";
  }

  if ($cmp_fs_rain < 0) {
    $cmp_fs_rain_color = "red";
  }
  elsif ($cmp_fs_rain > 0) {
    $cmp_fs_rain_color = "blue";
  }

}
else {
  $comp        = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm / 10))) + ((10 ** (-$eifm / 10))) + ((10 ** (-$aifm / 10))));
  $comp_itm    = -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$tfm_itm / 10))) + ((10 ** (-$eifm / 10))) + ((10 ** (-$aifm / 10))));
  $cmp_fs      = sprintf "%.2f", $comp;
  $comp_fs     = sprintf "%.2f", $comp;
  $cmp_itm     = sprintf "%.2f", $comp_itm;
  $comp_fs_itm = sprintf "%.2f", $comp_itm;
  $dfm_fs      = sprintf "%.2f", $dfm;
  $eifm_fs     = sprintf "%.2f", $eifm;
  $aifm_fs     = sprintf "%.2f", $aifm;

  if ($do_div eq "no") {
    $cmp_div_itm = "Not Applicable";
	$cmp_div_itm_color = "blue";
    $cmp_div_itm_rain = "Not Applicable";
    $cmp_div_itm_rain_color = "blue";
  }
  elsif ($do_div eq "yes") {
    $cmp_div_itm = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm / 10))) + ((10 ** (-$eifm / 10))) + ((10 ** (-$aifm / 10))));
    $cmp_div_itm_rain = sprintf "%.2f", -10 * log10(((10 ** (-$dfm / 10))) + ((10 ** (-$div_tfm_itm_rain / 10))) + ((10 ** (-$eifm / 10))) + ((10 ** (-$aifm / 10))));


  }

   if ($cmp_itm < 0) {
    $cmp_itm_color = "red";
  }
  elsif ($cmp_itm > 0) {
    $cmp_itm_color = "blue";
  }

  if ($cmp_itm_rain < 0) {
    $cmp_itm_rain_color = "red";
  }
  elsif ($cmp_itm_rain > 0) {
    $cmp_itm_rain_color = "blue";
  }

  if ($cmp_fs < 0) {
    $cmp_fs_color = "red";
  }
  elsif ($cmp_fs > 0) {
    $cmp_fs_color = "blue";
  }

  if ($cmp_fs_rain < 0) {
    $cmp_fs_rain_color = "red";
  }
  elsif ($cmp_fs_rain > 0) {
    $cmp_fs_rain_color = "blue";
  }

}

#################################################################################
#################################################################################
## North American Outage Calculations - Vigants
#
## One-Way - WITHOUT Spaced Vertical Antenna Diversity (Vigants/Free-Space)
# AAA
# One-way probability of outage (SES/year) for a non-diversity path
$Und_nodiv_fs = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_fs / 10);
$Und_nodiv_fs_per = 100 * (1 - $Und_nodiv_fs);
$Und_nodiv_fs_rain = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_fs_rain / 10); 
$Und_nodiv_fs_per_rain = 100 * (1 - $Und_nodiv_fs_rain);

if ($Und_nodiv_fs_per <= 0) {
  $Und_nodiv_fs_per = 0.00000000000;
}

if ($Und_nodiv_fs_per > 100) {
  $Und_nodiv_fs_per = 99.9999999999;
}

if ($Und_nodiv_fs_per_rain <= 0) {
  $Und_nodiv_fs_per_rain = 0.00000000000;
}

if ($Und_nodiv_fs_per_rain > 100) {
  $Und_nodiv_fs_per_rain = 99.9999999999;
}

# Bell System short-haul one-way outage objective, SES/year
$obj_nodiv_fs = 1600 * ($dist_mi / 250);
$obj_nodiv_fs_per = 100 - (100 * ($obj_nodiv_fs / 31557600));
$obj_nodiv_fs_two = (1600 * ($dist_mi / 250)) * 2;
$obj_nodiv_fs_per_two = 100 - (100 * ($obj_nodiv_fs_two / 31557600));

if ($obj_nodiv_fs_per <= 0) {
  $obj_nodiv_fs_per = 0.00000000000;
}

if ($obj_nodiv_fs_per > 100) {
  $obj_nodiv_fs_per = 99.9999999999;
}

if ($obj_nodiv_fs_per_two <= 0) {
  $obj_nodiv_fs_per_two = 0.00000000000;
}

if ($obj_nodiv_fs_per_two > 100) {
  $obj_nodiv_fs_per_two = 99.9999999999;
}

$obj_nodiv_fs_cfm = abs(log10(($obj_nodiv_fs / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj_nodiv_fs_cfm = sprintf "%.2f", $obj_nodiv_fs_cfm;
$obj_nodiv_fs_cfm_two = abs(log10(($obj_nodiv_fs_two / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj_nodiv_fs_cfm_two = sprintf "%.2f", $obj_nodiv_fs_cfm_two;

# Bell System long-haul one-way outage objective, SES/year
#$obj1_nodiv_fs = 1600 * ($dist_mi / 2000);
$obj1_nodiv_fs = 1600 * ($dist_mi / 4000);
$obj1_nodiv_fs_per = 100 - (100 * ($obj1_nodiv_fs / 31557600));
#$obj1_nodiv_fs_two = (1600 * ($dist_mi / 2000)) * 2;
$obj1_nodiv_fs_two = (1600 * ($dist_mi / 4000)) * 2;
$obj1_nodiv_fs_per_two = 100 - (100 * ($obj1_nodiv_fs_two / 31557600));

if ($obj1_nodiv_fs_per <= 0) {
  $obj1_nodiv_fs_per = 0.00000000000;
}

if ($obj1_nodiv_fs_per > 100) {
  $obj1_nodiv_fs_per = 99.9999999999;
}

if ($obj1_nodiv_fs_per_two <= 0) {
  $obj1_nodiv_fs_per_two = 0.00000000000;
}

if ($obj1_nodiv_fs_per_two > 100) {
  $obj1_nodiv_fs_per_two = 99.9999999999;
}

$obj1_nodiv_fs_cfm = abs(log10(($obj1_nodiv_fs / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj1_nodiv_fs_cfm = sprintf "%.2f", $obj1_nodiv_fs_cfm;
$obj1_nodiv_fs_cfm_two = abs(log10(($obj1_nodiv_fs_two / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj1_nodiv_fs_cfm_two = sprintf "%.2f", $obj1_nodiv_fs_cfm_two;

# ITU-R high-grade reference one-way outage objective, SES/year
$obj2_nodiv_fs = ((0.00054 * ($dist_km / 2500)) * 2680000) * 3 * ($temp_f / 50);
$obj2_nodiv_fs_per = 100 - (100 * ($obj2_nodiv_fs / 31557600));
$obj2_nodiv_fs_two = (((0.00054 * ($dist_km / 2500)) * 2680000) * 3 * ($temp_f / 50)) * 2;
$obj2_nodiv_fs_per_two = 100 - (100 * ($obj2_nodiv_fs_two / 31557600));

if ($obj2_nodiv_fs_per <= 0) {
  $obj_nodiv_fs_per = 0.00000000000;
}

if ($obj2_nodiv_fs_per > 100) {
  $obj2_nodiv_fs_per = 99.9999999999;
}

if ($obj2_nodiv_fs_per_two <= 0) {
  $obj_nodiv_fs_per_two = 0.00000000000;
}

if ($obj2_nodiv_fs_per_two > 100) {
  $obj2_nodiv_fs_per_two = 99.9999999999;
}

$obj2_nodiv_fs_cfm = abs(log10(($obj2_nodiv_fs / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj2_nodiv_fs_cfm = sprintf "%.2f", $obj2_nodiv_fs_cfm;
$obj2_nodiv_fs_cfm_two = abs(log10(($obj2_nodiv_fs_two / (0.4 * $cli_vig * $frq_ghz * $temp_f * ($dist_mi ** 3)))) * 10);
$obj2_nodiv_fs_cfm_two = sprintf "%.2f", $obj2_nodiv_fs_cfm_two;

# Annual outage, SES/yr, assume an approx 3 month fade season 
$SES_nodiv_fs_mo = $Und_nodiv_fs * 2680000; # SES per month (2680000 seconds)
$SES_nodiv_fs_yr = $SES_nodiv_fs_mo * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
$SES_nodiv_fs_per = 100 - (100 * ($SES_nodiv_fs_yr / 31557600));
$SES_nodiv_fs_mo_rain = $Und_nodiv_fs_rain * 2680000; # SES per month (2680000 seconds)
$SES_nodiv_fs_yr_rain = $SES_nodiv_fs_mo_rain * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
$SES_nodiv_fs_per_rain = 100 - (100 * ($SES_nodiv_fs_yr_rain / 31557600));

if ($SES_nodiv_fs_per <= 0) {
  $SES_nodiv_fs_per = "0.00000000000";
  $SES_nodiv_fs_yr = 31557600;
}

if ($SES_nodiv_fs_per >= 100) {
  $SES_nodiv_fs_per = "99.9999999999";
  $SES_nodiv_fs_yr = 0;
}

if ($SES_nodiv_fs_per_rain <= 0) {
  $SES_nodiv_fs_per_rain = "0.00000000000";
  $SES_nodiv_fs_yr_rain = 31557600;
}

if ($SES_nodiv_fs_per_rain >= 100) {
  $SES_nodiv_fs_per_rain = "99.9999999999";
  $SES_nodiv_fs_yr_rain = 0;
}

# Turn SES into minutes/hours/days
if ($SES_nodiv_fs_yr < 60) {
  $worst_nodiv_fs_yr =  sprintf "%.2f", $SES_nodiv_fs_yr;
  $worst_nodiv_fs_yr_val = "seconds";
}
elsif ($SES_nodiv_fs_yr >= 60 && $SES_nodiv_fs_yr < 3600) {
  $worst_nodiv_fs_yr =  sprintf "%.2f", $SES_nodiv_fs_yr / 60;
  $worst_nodiv_fs_yr_val = "minutes";
}
elsif ($SES_nodiv_fs_yr >= 3600 && $SES_nodiv_fs_yr < 86400) {
  $worst_nodiv_fs_yr =  sprintf "%.2f", $SES_nodiv_fs_yr / 3600;
  $worst_nodiv_fs_yr_val = "hours";

}
elsif ($SES_nodiv_fs_yr >= 86400) {
  $worst_nodiv_fs_yr =  sprintf "%.2f", $SES_nodiv_fs_yr / 86400;
  $worst_nodiv_fs_yr_val = "days";
}

# Turn SES into minutes/hours/days
if ($SES_nodiv_fs_yr_rain < 60) {
  $worst_nodiv_fs_yr_rain =  sprintf "%.2f", $SES_nodiv_fs_yr_rain;
  $worst_nodiv_fs_yr_val_rain = "seconds";
}
elsif ($SES_nodiv_fs_yr_rain >= 60 && $SES_nodiv_fs_yr_rain < 3600) {
  $worst_nodiv_fs_yr_rain =  sprintf "%.2f", $SES_nodiv_fs_yr_rain / 60;
  $worst_nodiv_fs_yr_val_rain = "minutes";
}
elsif ($SES_nodiv_fs_yr_rain >= 3600 && $SES_nodiv_fs_yr_rain < 86400) {
  $worst_nodiv_fs_yr_rain =  sprintf "%.2f", $SES_nodiv_fs_yr_rain / 3600;
  $worst_nodiv_fs_yr_val_rain = "hours";

}
elsif ($SES_nodiv_fs_yr_rain >= 86400) {
  $worst_nodiv_fs_yr_rain =  sprintf "%.2f", $SES_nodiv_fs_yr_rain / 86400;
  $worst_nodiv_fs_yr_val_rain = "days";
}

$SES_nodiv_fs_yr = sprintf "%.2f", $SES_nodiv_fs_yr;
$SES_nodiv_fs_per = sprintf "%.10f", $SES_nodiv_fs_per;
$SES_nodiv_fs_yr_rain = sprintf "%.2f", $SES_nodiv_fs_yr_rain;
$SES_nodiv_fs_per_rain = sprintf "%.10f", $SES_nodiv_fs_per_rain;
$obj_nodiv_fs = sprintf "%.2f", $obj_nodiv_fs;
$obj_nodiv_fs_per = sprintf "%.10f", $obj_nodiv_fs_per;
$obj_nodiv_fs_two = sprintf "%.2f", $obj_nodiv_fs_two;
$obj_nodiv_fs_per_two = sprintf "%.10f", $obj_nodiv_fs_per_two;
$obj1_nodiv_fs = sprintf "%.2f", $obj1_nodiv_fs;
$obj1_nodiv_fs_per = sprintf "%.10f", $obj1_nodiv_fs_per;
$obj1_nodiv_fs_two = sprintf "%.2f", $obj1_nodiv_fs_two;
$obj1_nodiv_fs_per_two = sprintf "%.10f", $obj1_nodiv_fs_per_two;
$obj2_nodiv_fs = sprintf "%.2f", $obj2_nodiv_fs;
$obj2_nodiv_fs_per = sprintf "%.10f", $obj2_nodiv_fs_per;
$obj2_nodiv_fs_two = sprintf "%.2f", $obj2_nodiv_fs_two;
$obj2_nodiv_fs_per_two = sprintf "%.10f", $obj2_nodiv_fs_per_two;
$Und_nodiv_fs_per = sprintf "%.10f", $Und_nodiv_fs_per;
$Und_nodiv_fs_per_rain = sprintf "%.10f", $Und_nodiv_fs_per_rain;

##############################################################################################################################
## One-Way - WITHOUT Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)
# BBB 
# One-way probability of outage (SES/year) for a non-diversity path
$Und_nodiv_itm          = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm / 10);
$Und_nodiv_itm_per      = 100 * (1 - $Und_nodiv_itm);
$Und_nodiv_itm_rain     = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm_rain / 10);
$Und_nodiv_itm_per_rain = 100 * (1 - $Und_nodiv_itm_rain);

if ($Und_nodiv_itm_per <= 0) {
  $Und_nodiv_itm_per = "0.00000000000";
}

if ($Und_nodiv_itm_per > 100) {
  $Und_nodiv_itm_per = "99.9999999999";
}

if ($Und_nodiv_itm_per_rain <= 0) {
  $Und_nodiv_itm_per_rain = "0.00000000000";
}

if ($Und_nodiv_itm_per_rain > 100) {
  $Und_nodiv_itm_per_rain = "99.9999999999";
}

# Annual outage, SES/yr, assume an approx 3 month fade season 
$SES_nodiv_itm_mo = $Und_nodiv_itm * 2680000; # SES per month (2680000 seconds)
$SES_nodiv_itm_yr = $SES_nodiv_itm_mo * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
$SES_nodiv_itm_per = 100 - (100 * ($SES_nodiv_itm_yr / 31557600));

$SES_nodiv_itm_mo_rain  = $Und_nodiv_itm_rain * 2680000; # SES per month (2680000 seconds)
$SES_nodiv_itm_yr_rain  = $SES_nodiv_itm_mo_rain * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
$SES_nodiv_itm_per_rain = 100 - (100 * ($SES_nodiv_itm_yr_rain / 31557600));

if ($SES_nodiv_itm_per <= 0) {
  $SES_nodiv_itm_per = "0.00000000000";
  $SES_nodiv_itm_yr = 31557600;
}

if ($SES_nodiv_itm_per > 100) {
  $SES_nodiv_itm_per = "99.9999999999";
  $SES_nodiv_itm_yr = 0;
}

if ($SES_nodiv_itm_per_rain <= 0) {
  $SES_nodiv_itm_per_rain = "0.00000000000";
  $SES_nodiv_itm_yr_rain = 31557600;
}

if ($SES_nodiv_itm_per_rain > 100) {
  $SES_nodiv_itm_per_rain = "99.9999999999";
  $SES_nodiv_itm_yr_rain = 0;
}

# Turn SES into minutes/hours/days - no rain
if ($SES_nodiv_itm_yr < 60) {
  $worst_nodiv_itm_yr =  sprintf "%.2f", $SES_nodiv_itm_yr;
  $worst_nodiv_itm_yr_val = "seconds";
}
elsif ($SES_nodiv_itm_yr >= 60 && $SES_nodiv_itm_yr < 3600) {
  $worst_nodiv_itm_yr =  sprintf "%.2f", $SES_nodiv_itm_yr / 60;
  $worst_nodiv_itm_yr_val = "minutes";
}
elsif ($SES_nodiv_itm_yr >= 3600 && $SES_nodiv_itm_yr < 86400) {
  $worst_nodiv_itm_yr =  sprintf "%.2f", $SES_nodiv_itm_yr / 3600;
  $worst_nodiv_itm_yr_val = "hours";

}
elsif ($SES_nodiv_itm_yr >= 86400) {
  $worst_nodiv_itm_yr =  sprintf "%.2f", $SES_nodiv_itm_yr / 86400;
  $worst_nodiv_itm_yr_val = "days";
}

# Turn SES into minutes/hours/days - rain
if ($SES_nodiv_itm_yr_rain < 60) {
  $worst_nodiv_itm_yr_rain =  sprintf "%.2f", $SES_nodiv_itm_yr_rain;
  $worst_nodiv_itm_yr_val_rain = "seconds";
}
elsif ($SES_nodiv_itm_yr_rain >= 60 && $SES_nodiv_itm_yr_rain < 3600) {
  $worst_nodiv_itm_yr_rain =  sprintf "%.2f", $SES_nodiv_itm_yr_rain / 60;
  $worst_nodiv_itm_yr_val_rain = "minutes";
}
elsif ($SES_nodiv_itm_yr_rain >= 3600 && $SES_nodiv_itm_yr_rain < 86400) {
  $worst_nodiv_itm_yr_rain =  sprintf "%.2f", $SES_nodiv_itm_yr_rain / 3600;
  $worst_nodiv_itm_yr_val_rain = "hours";

}
elsif ($SES_nodiv_itm_yr_rain >= 86400) {
  $worst_nodiv_itm_yr_rain =  sprintf "%.2f", $SES_nodiv_itm_yr_rain / 86400;
  $worst_nodiv_itm_yr_val_rain = "days";
}

$SES_nodiv_itm_yr       = sprintf "%.2f", $SES_nodiv_itm_yr;
$SES_nodiv_itm_per      = sprintf "%.10f", $SES_nodiv_itm_per;
$SES_nodiv_itm_yr_rain  = sprintf "%.2f", $SES_nodiv_itm_yr_rain;
$SES_nodiv_itm_per_rain = sprintf "%.10f", $SES_nodiv_itm_per_rain;

## Impossible Links
#
if ($tfm_itm <= 0) {
  $SES_nodiv_itm_yr = sprintf "%.2f", 31557600;
  $SES_nodiv_itm_per = sprintf "%.10f", 0;
  $worst_nodiv_itm_yr = "365.25";
  $worst_nodiv_itm_yr_val = "days";
}

if ($tfm_itm_rain <= 0) {
  $SES_nodiv_itm_yr_rain = sprintf "%.2f", 31557600;
  $SES_nodiv_itm_per_rain = sprintf "%.10f", 0;
  $worst_nodiv_itm_yr_rain = "365.25";
  $worst_nodiv_itm_yr_val_rain = "days";
}

if ($do_div eq "yes") {
  if ($div_tfm_itm <= 0) {
    $div_tfm_color = "red";
  }
  if ($div_tfm_itm_rain <= 0) {
    $div_tfm_color_rain = "red";
  }
}
elsif ($do_div eq "no") {
  $div_tfm_color = "blue";
  $div_tfm_color_rain = "blue";
}

## One-Way - WITH Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)
# DDD
# One-way probability of outage (SES/year) for a space diversity path
if ($do_div eq "yes") {
        
  # Vigants space diversity improvement factor
  # $V = 1 for same gain antennas
  if ($div_ant_dbi == $rx_ant_gain_dbi) {
    $V = 1; #$V = 1 for same gain antennas
  }
  else {
    if ($div_ant_dbi < 1.1) {
      $div_ant_dbi = 1.01;
    }
    if ($rx_ant_gain_dbi < 1.1) {
      $rx_ant_gain_dbi = 1.01;
    }

    $V = (20 * log10($div_ant_dbi)) / (20 * log10($rx_ant_gain_dbi));
  }
  
  # No Rain
  $Und_nodiv_itm = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm / 10);
  $Isd_itm = 7 * (10 ** -5) * $frq_ghz * ($V ** 2) * ($div_ft ** 2) * (10 ** ($cmp_div_itm / 10)) / $dist_mi;
  $Isd_itm_db = (10 * log10($frq_ghz)) + (20 * log10($div_ft)) - (10 * log($dist_mi)) - 41.55 + $cmp_div_itm;  
  $Isd_itm = sprintf "%.1f", $Isd_itm;
  $Isd_itm_db = sprintf "%.1f", $Isd_itm_db;

  if ($Isd_itm > 1.0) {
    
    $Isd_message_itm = "(Will Improve Reliability)";
    $Und_div_itm = $Und_nodiv_itm / $Isd_itm;

    # Annual outage, SES/yr, assume an approx 3 month fade season
    $SES_div_itm_mo = $Und_div_itm * 2680000; # SES per month (2680000 seconds)
    $SES_div_itm_yr = $SES_div_itm_mo * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
    $SES_div_itm_per = 100 - (100 * ($SES_div_itm_yr / 31557600));

    if ($SES_div_itm_per <= 0) {
     $SES_div_itm_per = 0.00000000000;
	 $SES_div_itm_yr = 31557600;
    }

    if ($SES_div_itm_per >= 100) {
      $SES_div_itm_per = 99.9999999999;
	  $SES_div_itm_yr = 0;
    }

	# Turn SES into minutes/hours/days
    if ($SES_div_itm_yr < 60) {
      $worst_div_itm_yr =  sprintf "%.2f", $SES_div_itm_yr;
      $worst_div_itm_yr_val = "seconds";
    }
    elsif ($SES_div_itm_yr >= 60 && $SES_div_itm_yr < 3600) {
      $worst_div_itm_yr =  sprintf "%.2f", $SES_div_itm_yr / 60;
      $worst_div_itm_yr_val = "minutes";
    }
    elsif ($SES_div_itm_yr >= 3600 && $SES_div_itm_yr < 86400) {
      $worst_div_itm_yr =  sprintf "%.2f", $SES_div_itm_yr / 3600;
      $worst_div_itm_yr_val = "hours";
    }
    elsif ($SES_div_itm_yr >= 86400) {
      $worst_div_itm_yr =  sprintf "%.2f", $SES_div_itm_yr / 86400;
      $worst_div_itm_yr_val = "days";
    }

	$SES_div_itm_yr = sprintf "%.2f", $SES_div_itm_yr;
    $SES_div_itm_per = sprintf "%.10f", $SES_div_itm_per;
	$Isd_color = "blue";
  }
  elsif ($Isd_itm <= 1.0) {
    # Use One-Way - WITHOUT Spaced Vertical Antenna Diversity (Vigants/ITWOMv3) values
    $Isd_message_itm = "(Will Not Improve Reliability)";
	$Isd_itm = sprintf "%.1f", $Isd_itm;
	$Isd_itm_db = sprintf "%.1f", $Isd_itm_db;
    $SES_div_itm_yr = $SES_nodiv_itm_yr;
    $SES_div_itm_per = $SES_nodiv_itm_per;
    $worst_div_itm_yr = $worst_nodiv_itm_yr; 
    $worst_div_itm_yr_val = $worst_nodiv_itm_yr_val;
	$Isd_color = "red";
  }
  
  # With Rain

  $Und_nodiv_itm_rain = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm_rain / 10);
  $Isd_itm_rain = 7 * (10 ** -5) * $frq_ghz * ($V ** 2) * ($div_ft ** 2) * (10 ** ($cmp_itm_rain / 10)) / $dist_mi;
  $Isd_itm_db_rain = (10 * log10($frq_ghz)) + (20 * log10($div_ft)) - (10 * log($dist_mi)) - 41.55 + $cmp_itm_rain;
  $Isd_itm_rain = sprintf "%.1f", $Isd_itm_rain;
  $Isd_itm_db_rain = sprintf "%.1f", $Isd_itm_db_rain;

  if ($Isd_itm_rain > 1.0) {

    $Isd_message_itm_rain = "(Will Improve Reliability)";
    $Und_div_itm_rain = $Und_nodiv_itm_rain / $Isd_itm_rain;

    # Annual outage, SES/yr, assume an approx 3 month fade season
    $SES_div_itm_mo_rain = $Und_div_itm_rain * 2680000; # SES per month (2680000 seconds)
    $SES_div_itm_yr_rain = $SES_div_itm_mo_rain * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
    $SES_div_itm_per_rain = 100 - (100 * ($SES_div_itm_yr_rain / 31557600));

    if ($SES_div_itm_per_rain <= 0) {
     $SES_div_itm_per_rain = 0.00000000000;
     $SES_div_itm_yr_rain = 31557600;
    }

    if ($SES_div_itm_per_rain >= 100) {
      $SES_div_itm_per_rain = 99.9999999999;
      $SES_div_itm_yr_rain = 0;
    }

    # Turn SES into minutes/hours/days
    if ($SES_div_itm_yr_rain < 60) {
      $worst_div_itm_yr_rain =  sprintf "%.2f", $SES_div_itm_yr_rain;
      $worst_div_itm_yr_val_rain = "seconds";
    }
    elsif ($SES_div_itm_yr_rain >= 60 && $SES_div_itm_yr_rain < 3600) {
      $worst_div_itm_yr_rain =  sprintf "%.2f", $SES_div_itm_yr_rain / 60;
      $worst_div_itm_yr_val_rain = "minutes";
    }
    elsif ($SES_div_itm_yr_rain >= 3600 && $SES_div_itm_yr_rain < 86400) {
      $worst_div_itm_yr_rain =  sprintf "%.2f", $SES_div_itm_yr_rain / 3600;
      $worst_div_itm_yr_val_rain = "hours";
    }
    elsif ($SES_div_itm_yr_rain >= 86400) {
      $worst_div_itm_yr_rain =  sprintf "%.2f", $SES_div_itm_yr_rain / 86400;
      $worst_div_itm_yr_val_rain = "days";
    }

    $Isd_itm_rain = sprintf "%.1f", $Isd_itm_rain;
	$Isd_itm_db_rain = sprintf "%.1f", $Isd_itm_db_rain;
    $SES_div_itm_yr_rain = sprintf "%.2f", $SES_div_itm_yr_rain;
    $SES_div_itm_per_rain = sprintf "%.10f", $SES_div_itm_per_rain;
	$Isd_color_rain = "blue";

  }
  elsif ($Isd_itm_rain <= 1.0) {
    # Use One-Way - WITHOUT Spaced Vertical Antenna Diversity (Vigants/ITWOMv3) values
    $Isd_message_itm_rain = "(Will Not Improve Reliability)";
    $SES_div_itm_yr_rain = $SES_nodiv_itm_yr_rain;
    $SES_div_itm_per_rain = $SES_nodiv_itm_per_rain;
    $worst_div_itm_yr_rain = $worst_nodiv_itm_yr_rain; 
    $worst_div_itm_yr_val_rain = $worst_nodiv_itm_yr_val_rain;
	$Isd_color_rain = "red";
  }
}
elsif ($do_div eq "no") {
  $Isd_itm = "Not Applicable";
  $Isd_message_itm = "";
  $Isd_itm_db_rain = "N/A";
  $Isd_itm_db = "N/A";
  $SES_div_itm_yr = "Not Applicable";
  $SES_div_itm_per = "Not Applicable";
  $worst_div_itm_yr = "Not Applicable";
  $worst_div_itm_yr_val = "";
  $Isd_itm_rain = "Not Applicable";
  $Isd_message_itm_rain = "";
  $SES_div_itm_yr_rain = "Not Applicable";
  $SES_div_itm_per_rain = "Not Applicable";
  $worst_div_itm_yr_rain = "Not Applicable";
  $worst_div_itm_yr_val_rain = "";
  $Isd_color = "blue";
  $Isd_color_rain = "blue";
}

## Frequency Diversity Improvement Factor - Vigants
# EEE
#
if ($frq_ghz_div >= 0.020 && $frq_ghz_div <= 2.0) {
		
  # Frequency diversity is mostly used above 2 GHz
  $do_frq_div = "no";
  $frq_ghz_div = "(Must Be Above 2 GHz)";
  $Ifd_itm = "Not Applicable";
  $Ifd_message_itm = "";
  $Ifd_color = "blue";
  $df = "N/A";
}
elsif ($frq_ghz_div > 2.0) {

  $do_frq_div = "yes";

  $df = sprintf "%.4f", abs($frq_ghz_div - $frq_ghz);

  if ($df > 0.5) {
    $df = 0.5; # use 0.5 GHz deltaF
  }

  $df_mhz = sprintf "%.2f", $df * 1000;

  # No Rain
  $Ifd_itm = 50 * $df * (10 ** ($cmp_itm / 10)) / (($frq_ghz ** 2) * $dist_mi);

  if ($Ifd_itm > 1.0) {

    $Und_nodiv_itm = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm / 10);
    $Und_frq_div_itm = $Und_nodiv_itm / $Ifd_itm;
    $SES_frq_div_itm_per = 100 * (1 - $Und_frq_div_itm);
    $SES_frq_div_mo_itm = $Und_frq_div_itm * 2680000; # SES per month (2680000 seconds)
    $SES_frq_div_yr_itm =  $SES_frq_div_mo_itm * 3 * ($temp_f / 50); # SES per year over a 3-month fade season

	if ($SES_frq_div_itm_per <= 0) {
      $SES_frq_div_itm_per = sprintf "%.10f", 0.0;
	  $SES_frq_div_yr_itm = 31557600;
    }

    if ($SES_frq_div_itm_per >= 100) {
      $SES_frq_div_itm_per = sprintf "%.10f", 99.999999999;
	  $SES_frq_div_yr_itm = 0;
    }

	# Turn SES into minutes/hours/days
    if ($SES_frq_div_yr_itm < 60) {
      $worst_frq_div_mo_itm =  sprintf "%.2f", $SES_frq_div_yr_itm;
      $worst_frq_div_mo_itm_val = "seconds";
    }
    elsif ($SES_frq_div_yr_itm >= 60 && $SES_frq_div_yr_itm < 3600) {
      $worst_frq_div_mo_itm =  sprintf "%.2f", $SES_frq_div_yr_itm / 60;
      $worst_frq_div_mo_itm_val = "minutes";
    }
    elsif ($SES_frq_div_yr_itm >= 3600 && $SES_frq_div_yr_itm < 86400) {
      $worst_frq_div_mo_itm =  sprintf "%.2f", $SES_frq_div_yr_itm / 3600;
      $worst_frq_div_mo_itm_val = "hours";
    }
    elsif ($SES_frq_div_yr_itm >= 86400) {
      $worst_frq_div_mo_itm =  sprintf "%.2f", $SES_frq_div_yr_itm / 86400;
      $worst_frq_div_mo_itm_val = "days";
    }

	$SES_frq_div_itm_per = sprintf "%.10f", abs($SES_frq_div_itm_per);
	$SES_frq_div_yr_itm = sprintf "%.2f", $SES_frq_div_yr_itm;
    $Ifd_message_itm = "(Will Improve Reliability)";
    $Ifd_itm = sprintf "%.1f", $Ifd_itm;
	$Ifd_color = "blue";
  }
  elsif ($Ifd_itm < 1.0) {
    $Ifd_message_itm = "(Will Not Improve Reliability)";
    $Ifd_itm = sprintf "%.1f", $Ifd_itm;
	$Ifd_color = "red";
	$df_mhz = sprintf "%.2f", $df * 1000;
	$SES_frq_div_itm_per = $SES_nodiv_itm_per;
	$SES_frq_div_yr_itm = $SES_nodiv_itm_yr;
	$worst_frq_div_mo_itm = $worst_nodiv_itm_yr;
	$worst_frq_div_mo_itm_val = $worst_nodiv_itm_yr_val;
  }
  
  # With Rain
  $Ifd_itm_rain = 50 * $df * (10 ** ($cmp_itm_rain / 10)) / (($frq_ghz ** 2) * $dist_mi);

  if ($Ifd_itm_rain > 1.0) {

    $Und_nodiv_itm_rain = $cli_vig * ($frq_ghz / 4) * (10 ** -5) * ($dist_mi ** 3) * 10 ** -($cmp_itm_rain / 10);
    $Und_frq_div_itm_rain = $Und_nodiv_itm_rain / $Ifd_itm_rain;
    $SES_frq_div_itm_per_rain = 100 * (1 - $Und_frq_div_itm_rain);
    $SES_frq_div_mo_itm_rain = $Und_frq_div_itm_rain * 2680000; # SES per month (2680000 seconds)
    $SES_frq_div_yr_itm_rain =  $SES_frq_div_mo_itm_rain * 3 * ($temp_f / 50); # SES per year over a 3-month fade season

    if ($SES_frq_div_itm_per_rain <= 0) {
      $SES_frq_div_itm_per_rain = sprintf "%.10f", 0.0;
      $SES_frq_div_yr_itm_rain = 31557600;
    }

    if ($SES_frq_div_itm_per_rain >= 100) {
      $SES_frq_div_itm_per_rain = sprintf "%.10f", 99.999999999;
      $SES_frq_div_yr_itm_rain = 0;
    }

    # Turn SES into minutes/hours/days
    if ($SES_frq_div_yr_itm_rain < 60) {
      $worst_frq_div_mo_itm_rain =  sprintf "%.2f", $SES_frq_div_yr_itm_rain;
      $worst_frq_div_mo_itm_val_rain = "seconds";
    }
    elsif ($SES_frq_div_yr_itm_rain >= 60 && $SES_frq_div_yr_itm_rain < 3600) {
      $worst_frq_div_mo_itm_rain =  sprintf "%.2f", $SES_frq_div_yr_itm_rain / 60;
      $worst_frq_div_mo_itm_val_rain = "minutes";
    }
    elsif ($SES_frq_div_yr_itm_rain >= 3600 && $SES_frq_div_yr_itm_rain < 86400) {
      $worst_frq_div_mo_itm_rain =  sprintf "%.2f", $SES_frq_div_yr_itm_rain / 3600;
      $worst_frq_div_mo_itm_val_rain = "hours";
    }
    elsif ($SES_frq_div_yr_itm_rain >= 86400) {
      $worst_frq_div_mo_itm_rain =  sprintf "%.2f", $SES_frq_div_yr_itm_rain / 86400;
      $worst_frq_div_mo_itm_val_rain = "days";
    }

    $SES_frq_div_itm_per_rain = sprintf "%.10f", abs($SES_frq_div_itm_per_rain);
    $SES_frq_div_yr_itm_rain = sprintf "%.2f", $SES_frq_div_yr_itm_rain;
    $Ifd_message_itm_rain = "(Will Improve Reliability)";
    $Ifd_itm_rain = sprintf "%.1f", $Ifd_itm_rain;
    $Ifd_color_rain = "blue";
  }
  elsif ($Ifd_itm_rain < 1.0) {
    $Ifd_message_itm_rain = "(Will Not Improve Reliability)";
    $Ifd_itm_rain = sprintf "%.1f", $Ifd_itm_rain;
    $Ifd_color_rain = "red";
    $SES_frq_div_itm_per_rain = $SES_nodiv_itm_per_rain;
    $SES_frq_div_yr_itm_rain = $SES_nodiv_itm_yr_rain;
    $worst_frq_div_mo_itm_rain = $worst_nodiv_itm_yr_rain;
    $worst_frq_div_mo_itm_val_rain = $worst_nodiv_itm_yr_val_rain;
  }
}
else {
  $do_frq_div = "no";
  $frq_ghz_div = "Not Applicable";
  $df_mhz = "N/A";
  $Ifd_itm = "Not Applicable";
  $Ifd_message_itm = "";
  $Ifd_color = "blue";
  $SES_frq_div_yr_itm = "Not Applicable";
  $SES_frq_div_itm_per = "Not Applicable";
  $worst_frq_div_mo_itm = "Not Applicable";
  $worst_frq_div_mo_itm_val = "";
  $Ifd_itm_rain = "Not Applicable";
  $Ifd_color_rain = "blue";
  $Ifd_message_itm_rain = "";
  $SES_frq_div_yr_itm_rain = "Not Applicable";
  $SES_frq_div_itm_per_rain = "Not Applicable";
  $worst_frq_div_mo_itm_rain = "Not Applicable";
  $worst_frq_div_mo_itm_val_rain = "";
}

if ($do_frq_div eq "yes") {

  if ($do_div eq "yes") {
    # Hybrid (Space+Frequency) Improvement Factor
    $Ihd_itm = sprintf "%.1f", $Ifd_itm * $Isd_itm;  

    if ($Ihd_itm > 1) {

      $Und_hyb_div_itm = $Und_nodiv_itm / $Ihd_itm;
      $SES_hyb_div_itm_per = 100 * (1 - $Und_hyb_div_itm);
      $SES_hyb_div_mo_itm = $Und_hyb_div_itm * 2680000; # SES per month (2680000 seconds)
      $SES_hyb_div_yr_itm = $SES_hyb_div_mo_itm * 3 * ($temp_f / 50); # SES per year over a 3-month fade season
  
	  if ($SES_hyb_div_itm_per < 0) {
        $SES_hyb_div_itm_per = sprintf "%.10f", 0.0;
		$SES_hyb_div_yr_itm = 31557600;
      }

      if ($SES_hyb_div_itm_per > 100) {
        $SES_hyb_div_itm_per = sprintf "%.10f", 99.999999999;
		$SES_hyb_div_yr_itm = 0;
      }

	  # Turn SES into minutes/hours/days
      if ($SES_hyb_div_yr_itm < 60) {
        $worst_hyb_div_yr_itm =  sprintf "%.2f", $SES_hyb_div_yr_itm;
        $worst_hyb_div_yr_itm_val = "seconds";
      }
      elsif ($SES_hyb_div_yr_itm >= 60 && $SES_hyb_div_yr_itm < 3600) {
        $worst_hyb_div_yr_itm =  sprintf "%.2f", $SES_hyb_div_yr_itm / 60;
        $worst_hyb_div_yr_itm_val = "minutes";
      }
      elsif ($SES_hyb_div_yr_itm >= 3600 && $SES_hyb_div_yr_itm < 86400) {
        $worst_hyb_div_yr_itm =  sprintf "%.2f", $SES_hyb_div_yr_itm / 3600;
        $worst_hyb_div_yr_itm_val = "hours";
      }
      elsif ($SES_hyb_div_yr_itm >= 86400) {
        $worst_hyb_div_yr_itm =  sprintf "%.2f", $SES_hyb_div_yr_itm / 86400;
        $worst_hyb_div_yr_itm_val = "days";
      }

	  $SES_hyb_div_itm_per = sprintf "%.10f", abs($SES_hyb_div_itm_per);
      $SES_hyb_div_yr_itm = sprintf "%.2f", $SES_hyb_div_yr_itm;
	  $Ihd_itm = sprintf "%.1f", $Ihd_itm;
	  $Ihd_message = "(Will Improve Reliability)";
	  $Ihd_color = "blue";
    }
	elsif ($Ihd_itm < 1) {
	  $Ihd_message = "(Will Not Improve Reliability)";
	  $Ihd_itm = sprintf "%.1f", $Ihd_itm;
	  $SES_hyb_div_yr_itm = "Not Applicable";
	  $SES_hyb_div_itm_per = "Not Applicable";
	  $worst_hyb_div_yr_itm = "Not Applicable";
	  $worst_hyb_div_yr_itm_val = "";
	  $Ihd_color = "red";
    }
  }
  elsif ($do_div eq "no") {
    $SES_hyb_div_itm_per = "Not Applicable";
    $SES_hyb_div_yr_itm = "Not Applicable";
    $Ihd_itm = "Not Applicable";
    $Ihd_message = "";
    $worst_hyb_div_yr_itm = "Not Applicable";
    $worst_hyb_div_yr_itm_val = "";
	$Ihd_color = "blue";
  }
}

if ($do_frq_div eq "no") {
  $SES_hyb_div_itm_per = "Not Applicable";
  $SES_hyb_div_yr_itm = "Not Applicable";
  $Ihd_itm = "Not Applicable";
  $Ihd_message = "";
  $worst_hyb_div_yr_itm = "Not Applicable";
  $worst_hyb_div_yr_itm_val = "";
  $Ihd_color = "blue";
}

## Foliage Loss
# ITU
$depth = 5; # Foliage depth in meters
$foli_loss = 0.2 * ($frq_mhz ** 0.3) * ($depth ** 0.6); # Loss in dB
$foli_m  = sprintf "%.3f", ($foli_loss / 5); # Loss in dB/m
$foli_ft = sprintf "%.3f", ($foli_loss / 5) / 3.2808399;

## RF Safety - FCC Limits for General Population/Uncontrolled Exposure and Occupational/Controlled Exposure
#
if ($frq_mhz >= 0.3 && $frq_mhz <= 1.34) {
  $std1 = 100.0; # Power Density (S) mW/cm2 - General
  $std2 = 100.0; # Power Density (S) mW/cm2 - Occupational
}
elsif ($frq_mhz > 1.34 && $frq_mhz <= 30.0) {
  $std1 = 180.0 / ($frq_mhz ** 2); # Power Density (S) mW/cm2 - General
  $std2 = 900.0 / ($frq_mhz ** 2);
}
elsif ($frq_mhz > 30.0 && $frq_mhz <= 300.0) {
  $std1 = 0.2; # Power Density (S) mW/cm2 - General
  $std2 = 1.0;
}
elsif ($frq_mhz > 300.0 && $frq_mhz <= 1500.0) {
  $std1 = $frq_mhz / 1500; # Power Density (S) mW/cm2 - General
  $std2 = $frq_mhz / 300; 
}
elsif ($frq_mhz > 1500.0 && $frq_mhz < 100000.0) {
  $std1 = 1.0; # Power Density (S) mW/cm2 - General
  $std2 = 5.0;
}
else {
  $std1 = 1.0; # Power Density (S) mW/cm2 - General
  $std2 = 5.0;
}

$rf_safe_eirp    = $tx_ant_input_mw * (10 ** ($tx_ant_gain_dbi / 10));
$rf_safe_dx      = $tx_ant_ht_ft * 30.48; # ft to cm
$pwrdens         = (0.64 * $rf_safe_eirp) / (pi * ($rf_safe_dx ** 2));
$rf_safe_pwrdens = sprintf "%.4f", (($pwrdens * 10000) + 0.5) / 10000;

$dx1    = (sqrt((0.64 * $rf_safe_eirp) / ($std1 * pi))) / 30.48;
$dx1    = (($dx1 * 10) + 0.5) / 10;
$dx1_ft = sprintf "%.2f", $dx1;
$dx1_m  = sprintf "%.2f", $dx1 * 0.3048;
$std1   = sprintf "%.2f", ((($std1 * 100) + 0.5) / 100);

$dx2    = (sqrt((0.64 * $rf_safe_eirp) / ($std2 * pi))) / 30.48;
$dx2    = (($dx2 * 10) + 0.5) / 10;
$dx2_ft = sprintf "%.2f", $dx2;
$dx2_m  = sprintf "%.2f", $dx2 * 0.3048;
$std2   = sprintf "%.2f", ((($std2 * 100) + 0.5) / 100);

## Grazing Angle
#
$ae   = 6378.137 * $k; # Earth radius with k-factor, km
$gr_m = ($dist_km ** 2) / (4 * $ae * (($tx_ant_ht_ov_m / 1000) + ($rx_ant_ht_ov_m / 1000)));
$gr_c = abs($tx_ant_ht_ov_m - $rx_ant_ht_ov_m) / ($tx_ant_ht_ov_m + $rx_ant_ht_ov_m);        

$gr_x = ((3 * $gr_c) / 2) * sqrt(($gr_m * 3) / (($gr_m + 1) ** 3));
$gr_y = cos((pi / 3) + (1 / 3) * acos($gr_x));
$gr_b = (2 * sqrt(($gr_m + 1) / ($gr_m * 3))) * $gr_y;

$graze    = (($tx_ant_ht_ov_m + $rx_ant_ht_ov_m) / $dist_km) * ((1 - $gr_m) * (1 + ($gr_b ** 2)));
$graze_mr = sprintf "%.2f", $graze; # millirad
$graze_dg = sprintf "%.2f", $graze * 0.0572958; # millirad to degree

## Path Reflection Point
#
if ($k_str eq "Infinity") {
  if ($tx_ant_ht_ft >= $rx_ant_ht_ft) {
    $grazing_dis    = ($rx_ant_ht_ft / ($rx_ant_ht_ft + $tx_ant_ht_ft)) * $dist_mi;
	$grazing_k      = "Not Applicable";
    $grazing_dis_mi = sprintf "%.2f", $grazing_dis;
    $grazing_dis_km = sprintf "%.2f", $grazing_dis * 1.609344;
  }
  elsif ($rx_ant_ht_ft > $tx_ant_ht_ft) {
    $grazing_dis    = ($tx_ant_ht_ft / ($tx_ant_ht_ft + $rx_ant_ht_ft)) * $dist_mi;
	$grazing_k      = "Not Applicable";
    $grazing_dis_mi = sprintf "%.2f", $grazing_dis;
    $grazing_dis_km = sprintf "%.2f", $grazing_dis * 1.609344;
  }
}
else {
  if ($tx_ant_ht_ft >= $rx_ant_ht_ft) {
    $X = $rx_ant_ht_ft / ($dist_mi ** 2);
    $Y = $rx_ant_ht_ft / ($dist_mi ** 2);
    $grazing_k      = sprintf "%.2f", 1 / (1.5 * ($X + $Y + 2 * sqrt($X * $Y)));
    $grazing_dis    = (1 / (1 + sqrt($Y / $X))) * $dist_mi;
    $grazing_dis_mi = sprintf "%.2f", $grazing_dis;
    $grazing_dis_km = sprintf "%.2f", $grazing_dis * 1.609344;
  }
  elsif ($rx_ant_ht_ft > $tx_ant_ht_ft) {
    $X = $tx_ant_ht_ft / ($dist_mi ** 2);
    $Y = $rx_ant_ht_ft / ($dist_mi ** 2);
    $grazing_k      = sprintf "%.2f", 1 / (1.5 * ($X + $Y + 2 * sqrt($X * $Y)));
    $grazing_dis    = (1 / (1 + sqrt($Y / $X))) * $dist_mi;
    $grazing_dis_mi = sprintf "%.2f", $grazing_dis;
    $grazing_dis_km = sprintf "%.2f", $grazing_dis * 1.609344;
  }
}
## Ideal Fade Margin
#
$min_fade = log10(((0.9995 - 1) / (-2.5 * 2 * $cli_vig * $frq_ghz * ($dist_mi ** 3) * (10 ** -6)))) * -10;
$min_fade = sprintf "%.2f", abs($min_fade);

## Amplitude Dispersion Fading
# 
# From "Digital Microave Radio - Engineering Fundamentals" NEC, MSD-3003
# Relates to fading prediction on FDM/video (analog) links
if ($check4 eq "yes") {
  $fade_rough_calc_m = $rough_m;
}
elsif ($check4 eq "no") {
  if ($rough_calc_m < 6) {
    $fade_rough_calc_m = 6;
  }

  if ($rough_calc_m > 42) {
    $fade_rough_calc_m = 42;
  }
  else {
    $fade_rough_calc_m = $rough_calc_m;
  }
}

# ITM Non-Div - Without Rain Loss
$amp1 = 0.002088 * ((10 ** -($cmp_itm / 20)) ** 2) * $frq_ghz * ($dist_km ** 3) * ($fade_rough_calc_m ** -1.27) * $cli_vig;

if ($amp1 >= 99) {
  $amp1 = (100 - (2.37 * ($fade_rough_calc_m ** -1.27) * $cli_vig * (10 ** ($cmp_itm / 7.88)))) / log10($dist_km / 10);
}

# ITM Non-Div - With Rain Loss
$amp2 = 0.002088 * ((10 ** -($cmp_itm_rain / 20)) ** 2) * $frq_ghz * ($dist_km ** 3) * ($fade_rough_calc_m ** -1.27) * $cli_vig;

if ($amp2 >= 99) {
  $amp2 = (100 - (2.37 * ($fade_rough_calc_m ** -1.27) * $cli_vig * (10 ** ($cmp_itm_rain / 7.88)))) / log10($dist_km / 10);
}

# Free-Space Non-Div - Without Rain Loss
$amp3 = 0.002088 * ((10 ** -($cmp_fs / 20)) ** 2) * $frq_ghz * ($dist_km ** 3) * ($fade_rough_calc_m ** -1.27) * $cli_vig;

if ($amp3 >= 99) {
  $amp3 = (100 - (2.37 * ($fade_rough_calc_m ** -1.27) * $cli_vig * (10 ** ($cmp_fs / 7.88)))) / log10($dist_km / 10);
}

# Free-Space Non-Div - With Rain Loss
$amp4 = 0.002088 * ((10 ** -($cmp_fs_rain / 20)) ** 2) * $frq_ghz * ($dist_km ** 3) * ($fade_rough_calc_m ** -1.27) * $cli_vig;

if ($amp4 >= 99) {
  $amp4 = (100 - (2.37 * ($fade_rough_calc_m ** -1.27) * $cli_vig * (10 ** ($cmp_fs_rain / 7.88)))) / log10($dist_km / 10);
}

$amp1_fade_s = ($amp1 / 100) * 31557600;
$amp2_fade_s = ($amp2 / 100) * 31557600;
$amp3_fade_s = ($amp3 / 100) * 31557600;
$amp4_fade_s = ($amp4 / 100) * 31557600;

# Turn amplitude dispersion fade outage into minutes/hours/days
if ($amp1_fade_s < 60) {
  $worst_amp_fade  = sprintf "%.2f", $amp1_fade_s;
  $worst_amp_fade_val = "seconds";
}
elsif ($amp1_fade_s >= 60 && $amp1_fade_s < 3600) {
  $worst_amp_fade = sprintf "%.2f", $amp1_fade_s / 60;
  $worst_amp_fade_val = "minutes";
}
elsif ($amp1_fade_s >= 3600 && $amp1_fade_s < 86400) {
  $worst_amp_fade =  sprintf "%.2f", $amp1_fade_s / 3600;
  $worst_amp_fade_val = "hours";

}
elsif ($amp1_fade_s >= 86400) {
  $worst_amp_fade =  sprintf "%.2f", $amp1_fade_s / 86400;
  $worst_amp_fade_val = "days";
}

# Turn amplitude dispersion fade outage into minutes/hours/days
if ($amp2_fade_s < 60) {
  $worst_amp_fade_rain  = sprintf "%.2f", $amp2_fade_s;
  $worst_amp_fade_rain_val = "seconds";
}
elsif ($amp2_fade_s >= 60 && $amp2_fade_s < 3600) {
  $worst_amp_fade_rain = sprintf "%.2f", $amp2_fade_s / 60;
  $worst_amp_fade_rain_val = "minutes";
}
elsif ($amp2_fade_s >= 3600 && $amp2_fade_s < 86400) {
  $worst_amp_fade_rain =  sprintf "%.2f", $amp2_fade_s / 3600;
  $worst_amp_fade_rain_val = "hours";

}
elsif ($amp2_fade_s >= 86400) {
  $worst_amp_fade_rain =  sprintf "%.2f", $amp2_fade_s / 86400;
  $worst_amp_fade_rain_val = "days";
}

# Turn amplitude dispersion fade outage into minutes/hours/days
if ($amp3_fade_s < 60) {
  $worst_amp_fade_fs = sprintf "%.2f", $amp3_fade_s;
  $worst_amp_fade_fs_val = "seconds";
}
elsif ($amp3_fade_s >= 60 && $amp3_fade_s < 3600) {
  $worst_amp_fade_fs = sprintf "%.2f", $amp3_fade_s / 60;
  $worst_amp_fade_fs_val = "minutes";
}
elsif ($amp3_fade_s >= 3600 && $amp3_fade_s < 86400) {
  $worst_amp_fade_fs = sprintf "%.2f", $amp3_fade_s / 3600;
  $worst_amp_fade_fs_val = "hours";

}
elsif ($amp3_fade_s >= 86400) {
  $worst_amp_fade_fs = sprintf "%.2f", $amp3_fade_s / 86400;
  $worst_amp_fade_fs_val = "days";
}

# Turn amplitude dispersion fade outage into minutes/hours/days
if ($amp4_fade_s < 60) {
  $worst_amp_fade_fs_rain = sprintf "%.2f", $amp4_fade_s;
  $worst_amp_fade_fs_rain_val = "seconds";
}
elsif ($amp4_fade_s >= 60 && $amp4_fade_s < 3600) {
  $worst_amp_fade_fs_rain = sprintf "%.2f", $amp4_fade_s / 60;
  $worst_amp_fade_fs_rain_val = "minutes";
}
elsif ($amp4_fade_s >= 3600 && $amp4_fade_s < 86400) {
  $worst_amp_fade_fs_rain = sprintf "%.2f", $amp4_fade_s / 3600;
  $worst_amp_fade_fs_rain_val = "hours";

}
elsif ($amp4_fade_s >= 86400) {
  $worst_amp_fade_fs_rain = sprintf "%.2f", $amp4_fade_s / 86400;
  $worst_amp_fade_fs_rain_val = "days";
}

if ($do_div eq "yes") {
  # Space Diversity Improvement - ITM - Without Rain
  $X = (830 * $dist_km * (10 ** -($cmp_itm / 10))) / ($frq_ghz * $div_m * $div_m);
  $amp1_itm_div = ($amp1 * $X) / sqrt(1 + ($X * $X));

  $amp1_itm_div_s = ($amp1_itm_div / 100) * 31557600;

  # Turn amplitude dispersion fade outage into minutes/hours/days
  if ($amp1_itm_div_s < 60) {
    $worst_amp_fade_itm_div = sprintf "%.2f", $amp1_itm_div_s;
    $worst_amp_fade_itm_div_val = "seconds";
  }
  elsif ($amp1_itm_div_s >= 60 && $amp1_itm_div_s < 3600) {
    $worst_amp_fade_itm_div = sprintf "%.2f", $amp1_itm_div_s / 60;
    $worst_amp_fade_itm_div_val = "minutes";
  }
  elsif ($amp1_itm_div_s >= 3600 && $amp1_itm_div_s < 86400) {
    $worst_amp_fade_itm_div = sprintf "%.2f", $amp1_itm_div_s / 3600;
    $worst_amp_fade_itm_div_val = "hours";
  }
  elsif ($amp1_itm_div_s >= 86400) {
    $worst_amp_fade_itm_div = sprintf "%.2f", $amp1_itm_div_s / 86400;
    $worst_amp_fade_itm_div_val = "days";
  }
}


## Potential Upfade
#
# If two signals reach the receiver in phase, then the signal amplifies. This is called upfade
$upfade = sprintf "%.2f", (10 * log10($dist_mi)) - (0.03 * $dist_mi);

## Mean Time Delay
#
$time_delay = sprintf "%.2f", 0.7 * ($dist_km / 50) ** 1.3; # nanoseconds

## National Land Cover Map - Experimental
#
if ($do_lulc eq "yes") {

  $LULC_LAT1 = abs($LAT1);
  $LULC_LON1 = abs($LON1);

  # LOL
  mkdir "lib";
  system "/bin/cp /usr/splat/tvstudy/lib/ptelev.conf lib/ptelev.conf";
  system "/bin/cp /usr/splat/tvstudy/lib/ptelev lib/ptelev";
  system "ln -s /usr/splat/tvstudy/dbase dbase";

  open(F1, ">", "lulc.gp") or die "Can't open lulc.gp: $!\n";
  open(F2, "<", "profile2.gp") or die "Can't open profile2.gp: $!\n";
  while (<F2>) {
	chomp;
	($dist, $elev) = split;
	$step_km = $dist * 1.609344;

	if ($step_km == 0) {
      $step_km = 0.03;
    }

    chomp($coord = `lib/ptelev 13 $LULC_LAT1 $LULC_LON1 $step_km $AZSP`);
    ($lat, $lon) = split ',', $coord;
    chomp($land = `lib/ptelev 15 $lat $lon`);

    if ($land eq "Open Water") {
      $color = "0x486DA2";
    }
    elsif ($land eq "Perennial Ice/Snow") {
      $color = "0xE7EFFC";
    }
    elsif ($land eq "Developed, Low Intensity") {
      $color = "0xDC9881";
    }
    elsif ($land eq "Developed, Medium Intensity") {
      $color = "0xF10100";
    }
    elsif ($land eq "Developed, High Intensity") {
      $color = "0xAB0101";
    }
    elsif ($land eq "Developed, Open Space") {
      $color = "0xE1CDCE";
    }
    elsif ($land eq "Barren Land (Rock/Sand/Clay)") {
      $color = "0xB3AFA4";
    }
    elsif ($land eq "Deciduous Forest") {
      $color = "0x6BA966";
    }
    elsif ($land eq "Evergreen Forest") {
      $color = "0x1D6533";
    }
    elsif ($land eq "Mixed Forest") {
      $color = "0xBDCC93";
    }
    elsif ($land eq "Grassland/Herbaceous") {
      $color = "0xEDECCD";
    }
    elsif ($land eq "Shrub/Scrub") {
      $color = "0xD1BB82";
    }
    elsif ($land eq "Pasture/Hay") {
      $color = "0xDDD83E";
    }
    elsif ($land eq "Cultivated Crops") {
      $color = "0xAE7229";
    }
    elsif ($land eq "Woody Wetlands") {
      $color = "0xBBD7ED";
    }
    elsif ($land eq "Emergent Herbaceous Wetland") {
      $color = "0x71A4C1";
    }
    else {
      $color = "0xE1CDCE"; # Developed, Open Space
    }
	print F1 "$dist\t$elev\t$color\n";
  }

  open(F, ">", "splat3.gp") or die "Can't open splat3.gp: $!\n";
    print F "set clip\n";
	print F "set tics scale 2, 1\n";
	print F "set mytics 10\n";
	print F "set mxtics 20\n";
	print F "set tics out\n";
    print F "set border 3\n";
	print F "set key below enhanced font \"Helvetica,18\"\n";
	print F "set grid back xtics ytics mxtics mytics\n";
	print F "set yrange [($min_elev - 5) to ($ymax + 10)]\n";
	print F "set xrange [0.0 to $dist_mi]\n";
	print F "set encoding utf8\n";
    print F "set term pngcairo enhanced size 2000,1600\n";
    print F "set title \"{/:Bold Path Profile Between $tx_name and $rx_name\\nU.S. National Land Cover Data (2021)}\" font \"Helvetica,30\"\n";
    print F "set xlabel \"Distance Between {/:Bold $tx_name } and {/:Bold $rx_name } ($dist_mi miles)\\n\" font \"Helvetica,22\"\n";
	print F "set x2label \"Frequency: $frq_mhz MHz\t\tAzimuth: $AZSP\\U+00B0 TN / $AZSP_MN\\U+00B0 MN  ($AZLP\\U+00B0 TN / $AZLP_MN\\U+00B0 MN)\" font \"Helvetica,20\"\n";
    print F "set ylabel \"Elevation - Above Mean Sea Level (feet)\" font \"Helvetica,22\"\n";
    print F "set timestamp '%d-%b-%Y %H:%M CST' bottom font \"Helvetica\"\n";
	print F "set style fill solid\n";
    print F "set arrow from 0,$tx_elv_ft to 0,$tx_ant_ht_ov_ft head lw 3 size screen 0.008,45.0,30.0 filled\n";
    print F "set arrow from $dist_mi,$rx_elv_ft to $dist_mi,$rx_ant_ht_ov_ft head lw 3 size screen 0.008,45.0,30.0 filled\n";

    $G = sprintf "%.1f", $grazing_dis_mi;
    $G =~ s/\./\\./;
    $G = $G . "[0-9]";
    chomp($GV = `/usr/bin/grep '$G' profile2.gp | head -n 1`);
    ($gd, $ge) = split ' ', $GV;
   
	print F "set arrow from 0,$tx_ant_ht_ov_ft to $grazing_dis_mi,$ge nohead lw 1 lt 0 dashtype 3\n";
	print F "set arrow from $grazing_dis_mi,$ge to $dist_mi,$rx_ant_ht_ov_ft nohead lw 1 lt 0 dashtype 3\n";
    print F "set arrow from $grazing_dis_mi,$min_elev to $grazing_dis_mi,$ge front lw 6\n";
	print F "set label \"     Reflection Point\" front at $grazing_dis_mi,$ge left rotate by 90\n";
    print F "set label \"     $tx_ant_ht_ov_ft\" left front at 0,$tx_ant_ht_ov_ft\n";
    print F "set label \"Pri. $rx_ant_ht_ov_ft     \" right front at $dist_mi,$rx_ant_ht_ov_ft\n";
    print F "set label 'Lat: $LAT1_D\\U+00B0 $LAT1_M\\U+0027 $LAT1_S\" $LAT1_gnu' left at 0,graph 1.07\n";
    print F "set label 'Lon: $LON1_D\\U+00B0 $LON1_M\\U+0027 $LON1_S\" $LON1_gnu' left at 0,graph 1.05\n";
    print F "set label 'Gnd Elv: $tx_elv_ft ft' left at 0,graph 1.03\n";
    print F "set label 'Ant Hgt: $tx_ant_ht_ft ft' left at 0,graph 1.01\n";
    print F "set label 'Lat: $LAT2_D\\U+00B0 $LAT2_M\\U+0027 $LAT2_S\" $LAT2_gnu' right at $dist_mi,graph 1.07\n";
    print F "set label 'Lon: $LON2_D\\U+00B0 $LON2_M\\U+0027 $LON2_S\" $LON2_gnu' right at $dist_mi,graph 1.05\n";
    print F "set label 'Gnd Elv: $rx_elv_ft ft' right at $dist_mi,graph 1.03\n";
    print F "set label 'Ant Hgt: $rx_ant_ht_ft ft' right at $dist_mi,graph 1.01\n";
    print F "set output \"LULCProfile.png\"\n";
	print F "plot \"lulc.gp\" using 1:2:3 title \"Land Usage Terrain Profile\\nwith $k_str K-Factor\" with boxes lc rgb variable, \"reference.gp\" title \"Reference Path\" with lines lt 1 lw 1 linecolor rgb \"blue\", \"fresnel.gp\" smooth csplines title \"First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"green\", \"fresnel_pt_6.gp\" smooth csplines title \"$fres% First Fresnel Zone\" lt 1 lw 1 linecolor rgb \"red\"\n";
  close F;
  &System($args = "$gnuplot splat3.gp >/dev/null 2>&1");
}

############################################################################################
## Print Output HTML
#
$outpdf = "$rx_name" . "-to-" . "$tx_name" . ".pdf";

print "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
print "<html><head>\n";
print "<title>Microwave Radio Path Analysis Results</title>\n";
print "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
print "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
print "<font face=\"Helvetica\">\n";
print "<center><table border=\"2\" cellpadding=\"8\"><tr><td align=\"center\" bgcolor=\"#7EBDE5\"><font size=\"6\"><b>Microwave Radio Path Analysis Results</b></font></td></tr></table></center>\n";

print "<center>\n";
print "<p><a href=\"tmp/$mon-$mday/$RAN/TerrainProfile.png\"><img src=\"tmp/$mon-$mday/$RAN/TerrainProfile.png\" height=\"480\" width=\"640\"></a>&nbsp;&nbsp;<a href=\"tmp/$mon-$mday/$RAN/ElevPro2.png\"><img src=\"tmp/$mon-$mday/$RAN/ElevPro2.png\" height=\"480\" width=\"640\"></a></p>\n";

if ($do_lulc eq "yes") {
  print "<p><a href=\"tmp/$mon-$mday/$RAN/LULCProfile.png\"><img src=\"tmp/$mon-$mday/$RAN/LULCProfile.png\" height=\"480\" width=\"640\"></a>&nbsp;&nbsp;<a href=\"https://www.mrlc.gov/sites/default/files/NLCDclasses.pdf\"><img src=\"../pics/NLCD_Colour_Classification_Update.jpg\" height=\"480\" width=\"640\"></a></p>\n";
}

print "<p><a href=\"tmp/$mon-$mday/$RAN/PathProfile1.png\"><img src=\"tmp/$mon-$mday/$RAN/PathProfile1.png\" height=\"480\" width=\"640\"></a>&nbsp;&nbsp;<a href=\"tmp/$mon-$mday/$RAN/ElevPro1.png\"><img src=\"tmp/$mon-$mday/$RAN/ElevPro1.png\" height=\"480\" width=\"640\"></a></p>\n";

if ($do_div eq "yes") {
  print "<p><a href=\"tmp/$mon-$mday/$RAN/PathProfile1-div.png\"><img src=\"tmp/$mon-$mday/$RAN/PathProfile1-div.png\" height=\"480\" width=\"640\"></a>&nbsp;&nbsp;<a href=\"tmp/$mon-$mday/$RAN/ElevPro1-div.png\"><img src=\"tmp/$mon-$mday/$RAN/ElevPro1-div.png\" height=\"480\" width=\"640\"></a></p>\n";
}

print "</center>\n";

print "<br><br><center>\n";
print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Path Profile Report: $project</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Site Equipment Notes</b></td><td><font color=\"blue\">$tx_notes</font></td><td><font color=\"blue\">$rx_notes</font></td></tr>\n";
print "<tr><td align=\"right\"><b>(WGS84)&nbsp;&nbsp;Latitude</b></td><td><font color=\"blue\">$LAT1_D</font>&deg; <font color=\"blue\">$LAT1_M</font>' <font color=\"blue\">$LAT1_S</font>&quot; $LAT1_val&nbsp;&nbsp;(<font color=\"blue\">$LAT1</font>&deg;)</td><td><font color=\"blue\">$LAT2_D</font>&deg; <font color=\"blue\">$LAT2_M</font>' <font color=\"blue\">$LAT2_S</font>&quot; $LAT2_val&nbsp;&nbsp;(<font color=\"blue\">$LAT2</font>&deg;)</td></tr>\n";
print "<tr><td align=\"right\"><b>(WGS84)&nbsp;&nbsp;Longitude</b></td><td><font color=\"blue\">$LON1_D</font>&deg; <font color=\"blue\">$LON1_M</font>' <font color=\"blue\">$LON1_S</font>&quot; $LON1_val&nbsp;&nbsp;(<font color=\"blue\">$LON1_geo</font>&deg;)</td><td><font color=\"blue\">$LON2_D</font>&deg; <font color=\"blue\">$LON2_M</font>' <font color=\"blue\">$LON2_S</font>&quot; $LON2_val&nbsp;&nbsp;(<font color=\"blue\">$LON2_geo</font>&deg;)</td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Zone</b></td><td><font color=\"blue\">$utm_zone_tx</font></td><td><font color=\"blue\">$utm_zone_rx</font></td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Easting Coordinates</b></td><td><font color=\"blue\">$easting_tx</font></td><td><font color=\"blue\">$easting_rx</font></td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Northing Coordinates</b></td><td><font color=\"blue\">$northing_tx</font></td><td><font color=\"blue\">$northing_rx</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Local Ground Elevation (AMSL)</b></td><td><font color=\"blue\">$tx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_elv_m</font> meters)</td><td><font color=\"blue\">$rx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_elv_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Height (Center-of-Radiation)</b></td><td><font color=\"blue\">$tx_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_ht_m</font> meters)</td><td><font color=\"blue\">$rx_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_ant_ht_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Overall Antenna Height (AMSL)</b></td><td><font color=\"blue\">$tx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_ht_ov_m</font> meters)</td><td><font color=\"blue\">$rx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_ant_ht_ov_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/True_north\">True North</a> Azimuth</b></td><td><font color=\"blue\">$AZSP</font>&deg; to RX</td><td><font color=\"blue\">$AZLP</font>&deg; to TX</td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/North_magnetic_pole\">Magnetic North</a> Azimuth</b></td><td><font color=\"blue\">$AZSP_MN</font>&deg; to RX</td><td><font color=\"blue\">$AZLP_MN</font>&deg; to TX</td></tr>\n";
print "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Magnetic_declination\">Magnetic Declination</a></b></td><td><font color=\"blue\">$magdec_tx</font>&deg; $magdir_tx</td><td><font color=\"blue\">$magdec_rx</font>&deg; $magdir_rx</td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Type</b></td><td><font color=\"blue\">$tx_cab<br>$tx_cab_desc</font></td><td><font color=\"blue\">$rx_cab<br>$rx_cab_desc</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Length</b></td><td><font color=\"blue\">$tx_length_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_length_m</font> meters)</td><td><font color=\"blue\">$rx_length_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_length_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Loss Specification</b></td><td><font color=\"blue\">$tx_loss_per_100f</font> dB/100 feet&nbsp;&nbsp;(<font color=\"blue\">$tx_loss_per_100m</font> dB/100 meters)</td><td><font color=\"blue\">$rx_loss_per_100f</font> dB/100 feet&nbsp;&nbsp;(<font color=\"blue\">$rx_loss_per_100m</font> dB/100 meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Loss Specification</b></td><td><font color=\"blue\">$tx_loss_per_foot</font> dB/foot&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$tx_loss_per_meter</font> dB/meter)</td><td><font color=\"blue\">$rx_loss_per_foot</font> dB/foot&nbsp;&nbsp;(<font color=\"blue\">$rx_loss_per_meter</font> dB/meter)</td></tr>\n";
print "<tr><td align=\"right\"><b>Calculated Transmission Line Loss</b></td><td><font color=\"blue\">$tx_cab_loss</font> dB</td><td><font color=\"blue\">$rx_cab_loss</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Efficiency</b></td><td><font color=\"$tx_eff_color\">$tx_eff</font>%&nbsp;&nbsp;($tx_eff_message)</td><td><font color=\"$rx_eff_color\">$rx_eff</font>%&nbsp;&nbsp;($rx_eff_message)</td></tr>\n";
print "<tr><td align=\"right\"><b>Transmission Line Miscellaneous Loss</b></td><td><font color=\"blue\">$tx_misc_cab_loss</font> dB</td><td><font color=\"blue\">$rx_misc_cab_loss</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Total Transmission Line Loss</b></td><td><font color=\"blue\">$tx_total_cable_loss</font> dB</td><td><font color=\"blue\">$rx_total_cable_loss</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Miscellaneous Gain</b></td><td><font color=\"blue\">$tx_misc_gain</font> dB</td><td><font color=\"blue\">$rx_misc_gain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Model / Notes</b></td><td><font color=\"blue\">$tx_ant_notes</font></td><td><font color=\"blue\">$rx_ant_notes</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Gain</b></td><td><font color=\"blue\">$tx_ant_gain_dbi</font> dBi&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_gain_dbd</font> dBd)&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$tx_ant_gain_radome</font> dB)</td><td><font color=\"blue\">$rx_ant_gain_dbi</font> dBi&nbsp;&nbsp;(<font color=\"blue\">$rx_ant_gain_dbd</font> dBd)&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$rx_ant_gain_radome</font> dB)</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Mechanical Tilt</b></td><td><font color=\"blue\">$tilt_tr</font>&deg;</td><td><font color=\"blue\">$tilt_rt</font>&deg;</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna (Parabolic) 3 dB Beamwidth</b></td><td><font color=\"blue\">$tx_ant_bw</font>&deg;</td><td><font color=\"blue\">$rx_ant_bw</font>&deg;</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Coverage 3 dB Radius</b></td><td>Inner: <font color=\"blue\">$inner</font> miles&nbsp;&nbsp;&nbsp;&nbsp;Outer: <font color=\"blue\">$outer</font> miles</td><td></td></tr>\n";
print "<tr><td align=\"right\"><b>Highest Transmitted Frequency</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$frq_ghz</font> GHz&nbsp;&nbsp;(<font color=\"blue\">$frq_mhz</font> MHz)</td></tr>\n";
print "<tr><td align=\"right\"><b>RF Power Output - dBx</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$pwr_out_dbm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_dbw</font> dBW)&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_dbk</font> dBk)</td></tr>\n";
print "<tr><td align=\"right\"><b>RF Power Output - Watts</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$pwr_out_mw</font> mW&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_w</font> W)&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_kw</font> kW)</td></tr>\n";
print "<tr><td align=\"right\"><b>Wavelength</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$wav_in</font> inches&nbsp;&nbsp;(<font color=\"blue\">$wav_cm</font> cm)&nbsp;&nbsp;(<font color=\"blue\">$wav_ft</font> feet)&nbsp;&nbsp;(<font color=\"blue\">$wav_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Effective Isotropic Radiated Power (EIRP)</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$eirp</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$eirp_dbw</font> dBW)&nbsp;&nbsp;(<font color=\"blue\">$eirp_dbk</font> dBk)</td></tr>\n";
print "<tr><td align=\"right\"><b>Effective Isotropic Radiated Power (EIRP)</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$eirp_mw</font> mW&nbsp;&nbsp;(<font color=\"blue\">$eirp_w</font> W)&nbsp;&nbsp;(<font color=\"blue\">$eirp_kw</font> kW)</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Transmitter Site RF Safety</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>General</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Occupational</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Maximum Permissible Exposure</b></td><td><font color=\"blue\">$std1</font> mW/cm<sup>2</sup></td><td><font color=\"blue\">$std2</font> mW/cm<sup>2</sup></td></tr>\n";
print "<tr><td align=\"right\"><b>Distance to RF Safety Compliance</b></td><td><font color=\"blue\">$dx1_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$dx1_m</font> meters)</td><td><font color=\"blue\">$dx2_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$dx2_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\">(<a href=\"https://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet65/oet65.pdf\">FCC OET Bulletin 65</a>)&nbsp;&nbsp;<b>Estimated RF Power Density</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$rf_safe_pwrdens</font> mW/cm<sup>2</sup>&nbsp;&nbsp;&nbsp;&nbsp;(Directly Below the Radiating Antenna)</td></tr>\n";
print "<tr><td align=\"right\"><b>Total RF Input Power to the Antenna</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$tx_ant_input</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_input_mw</font> mW)</td></tr>\n";
print "<tr><td align=\"right\">(<a href=\"https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/subject-group-ECFR2f2e5828339709e/section-15.247\">FCC Part 15.247</a>)&nbsp;&nbsp;<b>Allowed RF Input Power to Antenna</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_ant_pwr</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$max_ant_pwr_mw</font> mW)</td></tr>\n";
print "<tr><td align=\"right\">(<a href=\"https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-74/subpart-F/section-74.644\">FCC Part 74.644</a>)&nbsp;&nbsp;<b>Maximum Allowable EIRP</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$fcc_eirp_dbm</font> dBm&nbsp;&nbsp;$fcc_check</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Terrain &amp; Atmospheric Conditions</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\" colspan=\"3\"><b><i>Specifications</i></b></td><tr>\n";

if ($check3 eq "no") {
  print "<tr><td align=\"right\"><b>Effective Earth Radius (K-Factor)</b></td><td colspan=\"2\"><font color=\"blue\">$k_str</font>&nbsp;&nbsp;(<font color=\"blue\">$k_dec</font> - $k_val)</td></tr>\n";
}

if ($check3 eq "yes") {
  print "<tr><td align=\"right\"><b>Effective Earth Radius (K-Factor)</b></td><td colspan=\"2\"><font color=\"blue\">$k_str</font>&nbsp;&nbsp;($k_val)&nbsp;&nbsp;&nbsp;&nbsp;(Local Elevation: <font color=\"blue\">$k_ht_ft</font> feet / <font color=\"blue\">$k_ht_m</font> m)</td></tr>\n";
}

print "<tr><td align=\"right\"><b>Grazing Angle</b></td><td colspan=\"2\"><font color=\"blue\">$graze_dg</font>&deg;&nbsp;&nbsp;(<font color=\"blue\">$graze_mr</font> milliradians)</td></tr>\n";
print "<tr><td align=\"right\"><b>Approximate Distance to Reflection Point</b></td><td colspan=\"2\"><font color=\"blue\">$grazing_dis_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$grazing_dis_km</font> kilometers)</td></tr>\n";
print "<tr><td align=\"right\"><b>Terrain Roughness (Supplied)</b></td><td colspan=\"2\"><font color=\"blue\">$rough_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rough_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Terrain Roughness (Calculated)</b></td><td colspan=\"2\"><font color=\"blue\">$rough_calc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rough_calc_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Average Annual Temperature</b></td><td colspan=\"2\"><font color=\"blue\">$temp_f</font>&deg; F&nbsp;&nbsp;(<font color=\"blue\">$temp_c</font>&deg; C)</td></tr>\n";
print "<tr><td align=\"right\"><b>Atmospheric Pressure (Sea Level Corrected)</b></td><td colspan=\"2\"><font color=\"blue\">$atmos_p</font> millibars</td></tr>\n";
print "<tr><td align=\"right\"><b>Saturation Vapor Pressure</b></td><td colspan=\"2\"><font color=\"blue\">$es</font> millibars</td></tr>\n";
print "<tr><td align=\"right\"><b>Partial Vapor Pressure</b></td><td colspan=\"2\"><font color=\"blue\">$vapor_p</font> millibars</td></tr>\n";
printf "<tr><td align=\"right\"><b>Ground Dielectric Constant</b></td><td colspan=\"2\"><font color=\"blue\">%.f</font></td></tr>\n", $diecon;
printf "<tr><td align=\"right\"><b>Ground Conductivity</b></td><td colspan=\"2\"><font color=\"blue\">%.3f</font> Siemens/meter</td></tr>\n", $earcon;
print "<tr><td align=\"right\"><b>Vigants-Barnett Climate Factor</b></td><td colspan=\"2\"><font color=\"blue\">$cli_vig</font>&nbsp;&nbsp;($cli_val)</td></tr>\n";
print "<tr><td align=\"right\"><b>Longley-Rice Climate Type</b></td><td colspan=\"2\"><font color=\"blue\">$climate</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Crane Rain Region</b></td><td colspan=\"2\"><font color=\"blue\">$region</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Local Area Humidity Type</b></td><td colspan=\"2\"><font color=\"blue\">$rough_hum</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Index of Surface Refraction</b></td><td colspan=\"2\"><font color=\"blue\">$nunits</font> N-units (parts per million)</td></tr>\n";
print "<tr><td align=\"right\"><b>Antenna Polarization</b></td><td colspan=\"2\"><font color=\"blue\">$polar</font></td></tr>\n";
print "<tr><td align=\"right\"><b>Longley-Rice Situation Variability</b></td><td colspan=\"2\"><font color=\"blue\">$sit</font>% Confidence</td></tr>\n";
print "<tr><td align=\"right\"><b>Longley-Rice Time Variability</b></td><td colspan=\"2\"><font color=\"blue\">$time</font>% Reliability</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Terrain Plotting Parameters</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Distance to the Radio Horizon</b></td><td><font color=\"blue\">$tx_rad_hor_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$tx_rad_hor_km</font> km)</td><td><font color=\"blue\">$rx_rad_hor_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$rx_rad_hor_km</font> km)</tr>\n";
print "<tr><td align=\"right\"><b>Path Minimum Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$min_elev_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$min_elev_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Path Average Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$avg_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$avg_ht_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Path Maximum Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_elev_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$max_elev_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Earth Bulge at Path Midpoint</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$bulge_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$bulge_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Maximum Fresnel Zone Radius</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_fres_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$max_fres_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Additional Ground Clutter</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$gc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$gc_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Region for Terrain Plotting</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$city</font>, <font color=\"blue\">$state</font>&nbsp;&nbsp;(<font color=\"blue\">$country</font>)</td></tr>\n";
print "<tr><td align=\"right\"><b>Ideal Distance With These Antenna Heights</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$distance_max_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$distance_max_km</font> km)</td></tr>\n";
print "<tr><td align=\"right\"><b>Total Path Distance</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$dist_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$dist_km</font> km)</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Free-Space, ITM, Atmospheric, Rain, Misc. Losses</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Temperate Climate Foliage Loss</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$foli_ft</font> dB/foot&nbsp;&nbsp;(<font color=\"blue\">$foli_m</font> dB/meter)&nbsp;&nbsp;(Dense, Dry, In-Leaf)</td></tr>\n";
print "<tr><td align=\"right\"><b>Crane Rain Model Attenuation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$crane_rain_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$crane_rain_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$crane_rain_att_km</font> dB/km)&nbsp;&nbsp;&nbsp;&nbsp;(Rain Rate: <font color=\"blue\">$rate</font> mm/hr)</td></tr>\n";
print "<tr><td align=\"right\"><b>NASA Simplified Rain Model Attenuation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$nasa_rain_att_total</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Effective Rain Path Distance</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$rain_eff_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$rain_eff_km</font> km)</td></tr>\n";
print "<tr><td align=\"right\"><b>Estimated Attenuation Due to Water Vapor</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$water_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$water_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$water_att_km</font> dB/km)&nbsp;&nbsp;&nbsp;&nbsp;(Vapor Density: <font color=\"blue\">$wvd</font> gm/m<sup>3</sup>)</td></tr>\n";
print "<tr><td align=\"right\"><b>Estimated Attenuation Due to Oxygen Loss</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$oxy_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$oxy_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$oxy_att_km</font> dB/km)</td></tr>\n";
print "<tr><td align=\"right\"><b>Miscellaneous Path Losses</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$tx_misc_loss</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#7EBDE5\"><b><i>Ideal vs. Realistic Expectations</i></b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Friis Free-Space Path Loss</b></td><td><font color=\"blue\">$fs</font> dB</td><td><font color=\"blue\">$fs_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>ITWOMv3 Primary Path Loss</b></td><td><font color=\"blue\">$itm</font> dB</td><td><font color=\"blue\">$itm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>ITWOMv3 Diversity Path Loss</b></td><td><font color=\"blue\">$div_itm</font> dB</td><td><font color=\"blue\">$div_itm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Total Atmospheric + Rain Path Losses</b></td><td><font color=\"blue\">$atmos_norain</font> dB</td><td><font color=\"blue\">$atmos_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Free-Space + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$fs_pl</font> dB</td><td><font color=\"blue\">$fs_pl_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>(Primary Path)&nbsp;&nbsp;ITWOMv3 + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$itm_pl</font> dB</td><td><font color=\"blue\">$itm_pl_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>(Diversity Path)&nbsp;&nbsp;ITWOMv3 + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$div_itm_pl</font> dB</td><td><font color=\"blue\">$div_itm_pl_rain</font> dB</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"5\"><b>Calculated Fade Margins</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Receiver Threshold</b></td><td></td><td><font color=\"blue\">$BER_dbm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$BER_uvolt</font> &micro;V)&nbsp;&nbsp;&nbsp;&nbsp;($BER_crit)</td></tr>\n";
print "<tr><td align=\"right\"><b>Dispersive Fade Margin</b></td><td>&nbsp;<td><font color=\"blue\">$dfm_fs</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>External Interference Fade Margin</b></td><td>&nbsp;</td><td><font color=\"blue\">$eifm_fs</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Adjacent Channel Interference Fade Margin</b></td><td>&nbsp;</td><td><font color=\"blue\">$aifm_fs</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Minimum Composite Fade Margin for This Climate</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$min_fade</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Potential Upfade</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$upfade</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Path Mean Time Delay</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$time_delay</font> nanoseconds</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#7EBDE5\"><b><i>Unfaded Values</i></b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Free-Space Loss Received Signal Level</b></td><td><font color=\"blue\">$rx_pwr</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_pwr_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_rain_uvolt</font> &micro;V)</td></tr>\n";
print "<tr><td align=\"right\"><b>Free-Space Thermal Fade Margin</b></td><td><font color=\"$tfm_color\">$tfm</font> dB</td><td><font color=\"$tfm_color_rain\">$tfm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>ITWOMv3 Loss Received Signal Level</b></td><td><font color=\"blue\">$rx_pwr_itm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_itm_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_pwr_itm_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_itm_rain_uvolt</font> &micro;V)</td></tr>\n";
print "<tr><td align=\"right\"><b>ITWOMv3 Thermal Fade Margin</b></td><td><font color=\"$tfm_itm_color\">$tfm_itm</font> dB</td><td><font color=\"$tfm_itm_color_rain\">$tfm_itm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>Space Diversity ITWOMv3 Received Signal Level</b></td><td><font color=\"blue\">$rx_div_pwr_itm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_div_pwr_itm_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_div_pwr_itm_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_div_pwr_itm_rain_uvolt</font> &micro;V)</td></tr>\n";
print "<tr><td align=\"right\"><b>Space Diversity ITWOMv3 Thermal Fade Margin</b></td><td><font color=\"$div_tfm_color\">$div_tfm_itm</font> dB</td><td><font color=\"$div_tfm_color_rain\">$div_tfm_itm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Free-Space Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_fs_color\">$cmp_fs</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_fs_rain_color\">$cmp_fs_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Non-Diverstiy ITWOMv3 Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_itm_color\">$cmp_itm</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_itm_rain_color\">$cmp_itm_rain</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Space Diversity ITWOMv3 Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_div_itm_color\">$cmp_div_itm</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_div_itm_rain_color\">$cmp_div_itm_rain</font> dB\</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"5\"><b>Vertical Space Diversity Antenna Parameters</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX-DIV)</b></td></tr>\n";
print "<tr><td align=\"right\"><b>Local Ground Elevation (AMSL)</b></td><td><font color=\"blue\">$rx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_elv_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>User Supplied Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_m</font> meters)&nbsp;&nbsp;&nbsp;&nbsp;$div_ft_check</td></tr>\n";
print "<tr><td align=\"right\"><b>Adjusted Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_calc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_calc_m</font> meters)&nbsp;&nbsp;&nbsp;&nbsp;(Odd Multiple 1/2&lambda;)</td></tr>\n";
print "<tr><td align=\"right\"><b>Calculated Ideal Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_space_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_space_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Diversity Antenna Height (AGL)</b></td><td><font color=\"blue\">$div_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_ant_ht_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Overall Diversity Receiver Antenna Height (AMSL)</b></td><td><font color=\"blue\">$div_rx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_rx_ant_ht_ov_m</font> meters)</td></tr>\n";
print "<tr><td align=\"right\"><b>Diversity Antenna Gain</b></td><td><font color=\"blue\">$div_ant_dbi</font> dBi&nbsp;&nbsp;(<font color=\"blue\">$div_ant_dbd</font> dBd)&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$rx_div_ant_gain_radome</font> dB)&nbsp;&nbsp;$div_gain_check</td></tr>\n";
print "<tr><td align=\"right\"><b>Diversity Antenna Mechanical Tilt</b></td><td><font color=\"blue\">$tilt_rtd</font>&deg; to TX</td></tr>\n";
print "</table><br><br>\n";

print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"5\"><b>Target Outage Objectives &amp; Probabilities</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Outage Objective</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Reliability</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Required Composite Fade Margin</b></td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Bell System Short-Haul</b></td><td><font color=\"blue\">$obj_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj_nodiv_fs_cfm</font> dB</td></tr>\n";   
print "<tr><td align=\"right\"><b>One-Way Bell System Long-Haul</b></td><td><font color=\"blue\">$obj1_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj1_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj1_nodiv_fs_cfm</font> dB</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way ITU-R High-Grade</b></td><td><font color=\"blue\">$obj2_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj2_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj2_nodiv_fs_cfm</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way Bell System Short-Haul</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_cfm_two</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way Bell System Long-Haul</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_cfm_two</font> dB</td></tr>\n";
print "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way ITU-R High-Grade</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_cfm_two</font> dB</td></tr>\n";
print "</table><br><br>\n";

# AAA
print "<table border=\"1\" cellspacing=\"0\" cellpadding=\"8\" width=\"70%\">\n";
print "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"5\"><b>Calculated Outage Objectives &amp; Probabilities</b></font></td></tr>\n";
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Without Spaced Vertical Antenna Diversity (Vigants/Free-Space)</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_nodiv_fs_yr</font> SES/year</td><td><font color=\"blue\">$SES_nodiv_fs_yr_rain</font> SES/year</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_nodiv_fs_per</font>%</td><td><font color=\"blue\">$SES_nodiv_fs_per_rain</font>%</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_nodiv_fs_yr</font>&nbsp;&nbsp;$worst_nodiv_fs_yr_val</td><td><font color=\"blue\">$worst_nodiv_fs_yr_rain</font>&nbsp;&nbsp;$worst_nodiv_fs_yr_val_rain</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Amplitude Dispersion Fading Outage</b></td><td><font color=\"blue\">$worst_amp_fade_fs</font> $worst_amp_fade_fs_val</td><td><font color=\"blue\">$worst_amp_fade_fs_rain</font> $worst_amp_fade_fs_val</td></tr>\n";

# BBB
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>Without Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_nodiv_itm_yr</font> SES/year</td><td><font color=\"blue\">$SES_nodiv_itm_yr_rain</font> SES/year</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_nodiv_itm_per</font>%</td><td><font color=\"blue\">$SES_nodiv_itm_per_rain</font>%</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_nodiv_itm_yr</font>&nbsp;&nbsp;$worst_nodiv_itm_yr_val</td><td><font color=\"blue\">$worst_nodiv_itm_yr_rain</font>&nbsp;&nbsp;$worst_nodiv_itm_yr_val_rain</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Amplitude Dispersion Fading Outage</b></td><td><font color=\"blue\">$worst_amp_fade</font> $worst_amp_fade_val</td><td><font color=\"blue\">$worst_amp_fade_rain</font> $worst_amp_fade_rain_val</td></tr>\n";

# DDD
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
print "<tr><td align=\"right\"><b>Space Diversity Improvement Factor</b></td><td><font color=\"$Isd_color\">$Isd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$Isd_itm_db</font> dB)&nbsp;&nbsp;&nbsp;&nbsp;$Isd_message_itm</td><td><font color=\"$Isd_color_rain\">$Isd_itm_rain</font>&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$Isd_itm_db_rain</font> dB)&nbsp;&nbsp;&nbsp;&nbsp;$Isd_message_itm_rain</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_div_itm_yr</font> SES/year</td><td><font color=\"blue\">$SES_div_itm_yr_rain</font> SES/year</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_div_itm_per</font>%</td><td><font color=\"blue\">$SES_div_itm_per_rain</font>%</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_div_itm_yr</font>&nbsp;&nbsp;$worst_div_itm_yr_val</td><td><font color=\"blue\">$worst_div_itm_yr_rain</font>&nbsp;&nbsp;$worst_div_itm_yr_val_rain</td></tr>\n";

# EEE
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Frequency Diversity (Vigants/ITWOMv3)</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
print "<tr><td align=\"right\"><b>Diversity Frequency</b></td><td colspan=\"2\"><font color=\"blue\">$frq_ghz_div</font> GHz&nbsp;&nbsp;&nbsp;&nbsp;(&Delta;F: <font color=\"blue\">$df_mhz</font> MHz)</td></tr>\n";
print "<tr><td align=\"right\"><b>Frequency Diversity Improvement Factor</b></td><td><font color=\"$Ifd_color\">$Ifd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ifd_message_itm</td><td><font color=\"$Ifd_color_rain\">$Ifd_itm_rain</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ifd_message_itm_rain</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_frq_div_yr_itm</font> SES/year</td><td><font color=\"blue\">$SES_frq_div_yr_itm_rain</font> SES/year</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_frq_div_itm_per</font>%</td><td><font color=\"blue\">$SES_frq_div_itm_per_rain</font>%</td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_frq_div_mo_itm</font>&nbsp;&nbsp;$worst_frq_div_mo_itm_val</td><td><font color=\"blue\">$worst_frq_div_mo_itm_rain</font>&nbsp;&nbsp;$worst_frq_div_mo_itm_val_rain</td></tr>\n";

# FFF
print "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Hybrid Diversity (Vigants/ITWOMv3)</i></b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
print "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
print "<tr><td align=\"right\"><b>Hybrid (Space + Frequency) Diversity Improvement Factor</b></td><td><font color=\"$Ihd_color\">$Ihd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ihd_message</td><td>&nbsp;</td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_hyb_div_yr_itm</font> SES/year</td><td></td></tr>\n";
print "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_hyb_div_itm_per</font>%</td><td></td></tr>\n";
print "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_hyb_div_yr_itm</font>&nbsp;&nbsp;$worst_hyb_div_yr_itm_val</td><td></td></tr>\n";
print "</table><br><br>\n";

# CCC
#print "\n<font color=\"maroon\"><b>&nbsp;&nbsp;&nbsp;&nbsp;<i>WITH</i> Spaced Vertical Antenna Diversity (Free-Space)</b></font>\n\n";
#print "<b>               Space Diversity Improvement Factor :</b> <font color=\"blue\">$Isd</font>  ($Isd_message)\n";
#print "<b>          One-Way Multipath Probability of Outage :</b> <font color=\"blue\">$SES_div_fs_yr</font> SES/year  (<font color=\"blue\">$SES_div_fs_per</font>%)\n";
#print "<b>        Annual Multipath Severely Errored Seconds :</b> <font color=\"blue\">$worst_div_fs_yr</font> $worst_div_fs_yr_val\n";

print "<table border=\"2\" cellpadding=\"8\"><tr><td colspan=\"10\" bgcolor=\"#7EBDE5\" align=\"center\"><font size=\"5\"><b>Terrain Analysis Reports</b></font></td></tr></table><br>\n";
print "<table border=\"1\" cellpadding=\"6\">\n";
print "<tr>\n";
print "<td bgcolor=\"#CCCCBB\">\n";
print "<pre><font size=\"4\">\n";
print "<font color=\"maroon\"><b><u>HAAT Calculation</u></b></font>\n\n";

open(F, "<", "$tx_name-site_report.txt") or die "Can't open file $tx_name-site_report.txt: $!\n";
while (<F>) {
  chomp $_;
  print "$_\n";
}
close F;

print "</font></pre></td></tr></table><br>\n";
print "<table border=\"1\" cellpadding=\"6\">\n";
print "<tr>\n";
print "<td bgcolor=\"#BBCCBB\">\n";
print "<pre><font size=\"4\">\n";
print "<font color=\"maroon\"><b><u>HAAT Calculation</u></b></font>\n\n";

open(F, "<", "$rx_name-site_report.txt") or die "Can't open file $rx_name-site_report.txt: $!\n";
while (<F>) {
  chomp $_;
  print "$_\n";
}
close F;
print "</font></pre></td></tr></table><br>\n";

if ($do_div eq "yes") {
  print "<table border=\"1\" cellpadding=\"6\">\n";
  print "<tr>\n";
  print "<td bgcolor=\"#BBCCBB\">\n";
  print "<pre><font size=\"4\">\n";
  print "<font color=\"maroon\"><b><u>HAAT Calculation</u></b></font>\n\n";
  open(F, "<", "$rx_div_name-site_report.txt") or die "Can't open file $rx_div_name-site_report.txt: $!\n";
  while (<F>) {
    chomp $_;
    print "$_\n";
  }
  close F;
  print "</font></pre></td></tr></table><br>\n";
}

print "<table border=\"1\" cellpadding=\"6\">\n";
print "<tr>\n";
print "<td bgcolor=\"#CCCCBB\">\n";
print "<pre><font size=\"4\">\n";
print "<font color=\"maroon\"><b><u>SPLAT! Path Profile Calculations</u></b></font>\n\n";

$found = 0;
open(F, "<", "$rx_name-to-$tx_name.txt") or die "Can't open file $rx_name-to-$tx_name.txt: $!\n";
while ($line = <F>) {
  chomp $line;
  if ($line =~ /Site Name/) {
    $found = 1;
  }

  if ($found) {
    print "$line\n";
  }
}
close F;

print "</font></pre></td></tr></table><br>\n";

if ($do_div eq "yes") {
  print "<table border=\"1\" cellpadding=\"6\">\n";
  print "<tr>\n";
  print "<td bgcolor=\"#CCCCBB\">\n";
  print "<pre><font size=\"4\">\n";
  print "<font color=\"maroon\"><b><u>SPLAT! Path Profile Calculations</u></b></font>\n\n";
  $found = 0;
  open(F, "<", "$rx_div_name-to-$tx_name.txt") or die "Can't open file $rx_div_name-to-$tx_name.txt: $!\n";
  while ($line = <F>) {
    chomp $line;
    if ($line =~ /Site Name/) {
      $found = 1;
    }

    if ($found) {
      print "$line\n";
    }
  }
  close F;
  print "</font></pre></td></tr></table><br>\n";
}

print "<table border=\"1\" cellpadding=\"6\">\n";
print "<tr>\n";
print "<td bgcolor=\"#BBCCBB\">\n";
print "<pre><font size=\"4\">\n";
print "<font color=\"maroon\"><b><u>SPLAT! Path Profile Calculations</u></b></font>\n\n";

$found = 0;
open(F, "<", "$tx_name-to-$rx_name.txt") or die "Can't open file $tx_name-to-$rx_name.txt: $!\n";
while ($line = <F>) {
  chomp $line;
  if ($line =~ /Site Name/) {
	$found = 1;
  }

  if ($found) {
    print "$line\n";
  }
}
close F;

print "</font></td></tr></table>\n";
print "<br><b>General Coverage Topographical Map<br>$country ($city, $state)</b><br><a href=\"tmp/$mon-$mday/$RAN/TopoMap.png\"><img src=\"tmp/$mon-$mday/$RAN/TopoMap.png\" height=\"480\" width=\"640\"></a>\n";

if ($do_div eq "no") {
  print "<br><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_name</font></b><br><a href=\"tmp/$mon-$mday/$RAN/LOSMap.png\"><img src=\"tmp/$mon-$mday/$RAN/LOSMap.png\" height=\"480\" width=\"640\"></a>\n";
}
elsif ($do_div eq "yes") {
  print "<br><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_name</font></b><br><a href=\"tmp/$mon-$mday/$RAN/LOSMap.png\"><img src=\"tmp/$mon-$mday/$RAN/LOSMap.png\" height=\"480\" width=\"640\"></a>\n";
  print "<br><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_div_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_div_name</font></b><br><a href=\"tmp/$mon-$mday/$RAN/LOSMap-div.png\"><img src=\"tmp/$mon-$mday/$RAN/LOSMap-div.png\" height=\"480\" width=\"640\"></a>\n";
}

print "<br><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $tx_name</b><br><a href=\"tmp/$mon-$mday/$RAN/LossMap1.png\"><img src=\"tmp/$mon-$mday/$RAN/LossMap1.png\" height=\"480\" width=\"640\"></a>\n";

if ($do_div eq "no") {
  print "<br><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_name</b><br><a href=\"tmp/$mon-$mday/$RAN/LossMap2.png\"><img src=\"tmp/$mon-$mday/$RAN/LossMap2.png\" height=\"480\" width=\"640\"></a>\n";
}
elsif ($do_div eq "yes") {
  print "<br><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_name</b><br><a href=\"tmp/$mon-$mday/$RAN/LossMap2.png\"><img src=\"tmp/$mon-$mday/$RAN/LossMap2.png\" height=\"480\" width=\"640\"></a>\n";
  print "<br><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_div_name</b><br><a href=\"tmp/$mon-$mday/$RAN/LossMap-div.png\"><img src=\"tmp/$mon-$mday/$RAN/LossMap-div.png\" height=\"480\" width=\"640\"></a>\n";
}

print "<br><br><a href=\"tmp/$mon-$mday/$RAN/$tx_name-to-$rx_name.kml\"><b>Google Earth KML File</b></a>\n";
print "<br><br><a href=\"tmp/$mon-$mday/$RAN/$outpdf\"><b>Microwave Radio Path Analysis PDF Report</b></a>\n";
print "<br><br><b>Links to USGS topoView :&nbsp;&nbsp;<a href=\"https://ngmdb.usgs.gov/topoview/viewer/#11/$LAT1/$LON1_geo\">$tx_name</a>&nbsp;&nbsp;-&nbsp;&nbsp;<a href=\"https://ngmdb.usgs.gov/topoview/viewer/#11/$LAT2/$LON2_geo\">$rx_name</a></b>\n";
print "<br><br><b>Links to OpenStreetMap :&nbsp;&nbsp;<a href=\"https://www.openstreetmap.org/?mlat=$LAT1&mlon=$LON1_geo#map=16/$LAT1/$LON1_geo\">$tx_name</a>&nbsp;&nbsp;-&nbsp;&nbsp;<a href=\"https://www.openstreetmap.org/?mlat=$LAT2&mlon=$LON2_geo#map=16/$LAT2/$LON2_geo\">$rx_name</a></b>\n";
print "<br><br><b>Links to Google Maps :&nbsp;&nbsp;<a href=\"https://www.google.com/maps/search/?api=1&query=$LAT1,$LON1_geo\">$tx_name</a>&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"https://www.google.com/maps/search/?api=1&query=$LAT2,$LON2_geo\">$rx_name</a></b>\n";
print "<br><br><font size=\"-1\"><a href=\"http://www.gbppr.net\">GBPPR RadLab</a> $ver</font><br><font color=\"red\"><b>EXPERIMENTAL</b></font>\n";
print "<br><br>\n";
print "<hr noshade size=\"10\">\n";
print "<h3><p><i>Knowledge is Power</i></p></h3>\n";
print "<hr noshade size=\"10\">\n";
print "</center></font></body></html>\n";

&flush(STDOUT);

## Print File HTML
#
open(F, ">", "index1.html") or die "Can't open index1.html: $!\n" ;
print F "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
print F "<html><head>\n";
print F "<title>Microwave Radio Path Analysis Results</title>\n";
print F "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
print F "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
print F "<font face=\"Helvetica\">\n";
print F "<center><table border=\"2\" cellpadding=\"8\"><tr><td align=\"center\" bgcolor=\"#7EBDE5\"><font size=\"6\"><b>Microwave Radio Path Analysis Results</b></font></td></tr></table></center>\n";
print F "<center>\n";
print F "<p><img src=\"TerrainProfile.png\" height=\"480\" width=\"640\"></p>\n";
print F "<p><img src=\"ElevPro2.png\" height=\"480\" width=\"640\"></p>\n";

if ($do_lulc eq "yes") {
  print F "<p><img src=\"LULCProfile.png\" height=\"480\" width=\"640\">\n";
  print F "<p><img src=\"../../../../pics/NLCD_Colour_Classification_Update.jpg\" height=\"300\"></p>\n";
}

print F "<p><img src=\"PathProfile1.png\" height=\"480\" width=\"640\">\n";
print F "<p><img src=\"ElevPro1.png\" height=\"480\" width=\"640\"></p>\n";

if ($do_div eq "yes") {
  print F "<p><img src=\"PathProfile1-div.png\" height=\"480\" width=\"640\">\n";
  print F "<p><img src=\"ElevPro1-div.png\" height=\"480\" width=\"640\"></p>\n";
}

print F "</center></font></body></html>\n";

open(F, ">", "index2.html") or die "Can't open index2.html: $!\n" ;
  print F "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
  print F "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
  print F "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
  print F "<font face=\"Helvetica\"><font size=\"-1\">\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Path Profile Report: $project</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Site Equipment Notes</b></td><td><font color=\"blue\">$tx_notes</font></td><td><font color=\"blue\">$rx_notes</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>(WGS84)&nbsp;&nbsp;Latitude</b></td><td><font color=\"blue\">$LAT1_D</font>&deg; <font color=\"blue\">$LAT1_M</font>' <font color=\"blue\">$LAT1_S</font>&quot; $LAT1_val&nbsp;&nbsp;(<font color=\"blue\">$LAT1</font>&deg;)</td><td><font color=\"blue\">$LAT2_D</font>&deg; <font color=\"blue\">$LAT2_M</font>' <font color=\"blue\">$LAT2_S</font>&quot; $LAT2_val&nbsp;&nbsp;(<font color=\"blue\">$LAT2</font>&deg;)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>(WGS84)&nbsp;&nbsp;Longitude</b></td><td><font color=\"blue\">$LON1_D</font>&deg; <font color=\"blue\">$LON1_M</font>' <font color=\"blue\">$LON1_S</font>&quot; $LON1_val&nbsp;&nbsp;(<font color=\"blue\">$LON1_geo</font>&deg;)</td><td><font color=\"blue\">$LON2_D</font>&deg; <font color=\"blue\">$LON2_M</font>' <font color=\"blue\">$LON2_S</font>&quot; $LON2_val&nbsp;&nbsp;(<font color=\"blue\">$LON2_geo</font>&deg;)</td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Zone</b></td><td><font color=\"blue\">$utm_zone_tx</font></td><td><font color=\"blue\">$utm_zone_rx</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Easting Coordinates</b></td><td><font color=\"blue\">$easting_tx</font></td><td><font color=\"blue\">$easting_rx</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Universal_Transverse_Mercator_coordinate_system\">UTM</a> Northing Coordinates</b></td><td><font color=\"blue\">$northing_tx</font></td><td><font color=\"blue\">$northing_rx</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Local Ground Elevation (AMSL)</b></td><td><font color=\"blue\">$tx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_elv_m</font> meters)</td><td><font color=\"blue\">$rx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_elv_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Height (Center-of-Radiation)</b></td><td><font color=\"blue\">$tx_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_ht_m</font> meters)</td><td><font color=\"blue\">$rx_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_ant_ht_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Overall Antenna Height (AMSL)</b></td><td><font color=\"blue\">$tx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_ht_ov_m</font> meters)</td><td><font color=\"blue\">$rx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_ant_ht_ov_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/True_north\">True North</a> Azimuth</b></td><td><font color=\"blue\">$AZSP</font>&deg; to RX</td><td><font color=\"blue\">$AZLP</font>&deg; to TX</td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/North_magnetic_pole\">Magnetic North</a> Azimuth</b></td><td><font color=\"blue\">$AZSP_MN</font>&deg; to RX</td><td><font color=\"blue\">$AZLP_MN</font>&deg; to TX</td></tr>\n";
  print F "<tr><td align=\"right\"><b><a href=\"https://en.wikipedia.org/wiki/Magnetic_declination\">Magnetic Declination</a></b></td><td><font color=\"blue\">$magdec_tx</font>&deg; $magdir_tx</td><td><font color=\"blue\">$magdec_rx</font>&deg; $magdir_rx</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Type</b></td><td><font color=\"blue\">$tx_cab<br>$tx_cab_desc</font></td><td><font color=\"blue\">$rx_cab<br>$rx_cab_desc</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Length</b></td><td><font color=\"blue\">$tx_length_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$tx_length_m</font> meters)</td><td><font color=\"blue\">$rx_length_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_length_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Loss Specification</b></td><td><font color=\"blue\">$tx_loss_per_100f</font> dB/100 feet&nbsp;&nbsp;(<font color=\"blue\">$tx_loss_per_100m</font> dB/100 meters)</td><td><font color=\"blue\">$rx_loss_per_100f</font> dB/100 feet&nbsp;&nbsp;(<font color=\"blue\">$rx_loss_per_100m</font> dB/100 meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Loss Specification</b></td><td><font color=\"blue\">$tx_loss_per_foot</font> dB/foot&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$tx_loss_per_meter</font> dB/meter)</td><td><font color=\"blue\">$rx_loss_per_foot</font> dB/foot&nbsp;&nbsp;(<font color=\"blue\">$rx_loss_per_meter</font> dB/meter)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Calculated Transmission Line Loss</b></td><td><font color=\"blue\">$tx_cab_loss</font> dB</td><td><font color=\"blue\">$rx_cab_loss</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Efficiency</b></td><td><font color=\"$tx_eff_color\">$tx_eff</font>%&nbsp;&nbsp;($tx_eff_message)</td><td><font color=\"$rx_eff_color\">$rx_eff</font>%&nbsp;&nbsp;($rx_eff_message)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Transmission Line Miscellaneous Loss</b></td><td><font color=\"blue\">$tx_misc_cab_loss</font> dB</td><td><font color=\"blue\">$rx_misc_cab_loss</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Total Transmission Line Loss</b></td><td><font color=\"blue\">$tx_total_cable_loss</font> dB</td><td><font color=\"blue\">$rx_total_cable_loss</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Miscellaneous Gain</b></td><td><font color=\"blue\">$tx_misc_gain</font> dB</td><td><font color=\"blue\">$rx_misc_gain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Model / Notes</b></td><td><font color=\"blue\">$tx_ant_notes</font></td><td><font color=\"blue\">$rx_ant_notes</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Gain</b></td><td><font color=\"blue\">$tx_ant_gain_dbi</font> dBi&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$tx_ant_gain_radome</font> dB)</td><td><font color=\"blue\">$rx_ant_gain_dbi</font> dBi&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$rx_ant_gain_radome</font> dB)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Mechanical Tilt</b></td><td><font color=\"blue\">$tilt_tr</font>&deg;</td><td><font color=\"blue\">$tilt_rt</font>&deg;</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna (Parabolic) 3 dB Beamwidth</b></td><td><font color=\"blue\">$tx_ant_bw</font>&deg;</td><td><font color=\"blue\">$rx_ant_bw</font>&deg;</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Coverage 3 dB Radius</b></td><td>Inner: <font color=\"blue\">$inner</font> miles&nbsp;&nbsp;&nbsp;&nbsp;Outer: <font color=\"blue\">$outer</font> miles</td><td></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Highest Transmitted Frequency</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$frq_ghz</font> GHz&nbsp;&nbsp;(<font color=\"blue\">$frq_mhz</font> MHz)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>RF Power Output - dBx</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$pwr_out_dbm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_dbw</font> dBW)&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_dbk</font> dBk)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>RF Power Output - Watts</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$pwr_out_mw</font> mW&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_w</font> W)&nbsp;&nbsp;(<font color=\"blue\">$pwr_out_kw</font> kW)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Wavelength</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$wav_in</font> inches&nbsp;&nbsp;(<font color=\"blue\">$wav_cm</font> cm)&nbsp;&nbsp;(<font color=\"blue\">$wav_ft</font> feet)&nbsp;&nbsp;(<font color=\"blue\">$wav_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Effective Isotropic Radiated Power (EIRP)</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$eirp</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$eirp_dbw</font> dBW)&nbsp;&nbsp;(<font color=\"blue\">$eirp_dbk</font> dBk)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Effective Isotropic Radiated Power (EIRP)</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$eirp_mw</font> mW&nbsp;&nbsp;(<font color=\"blue\">$eirp_w</font> W)&nbsp;&nbsp;(<font color=\"blue\">$eirp_kw</font> kW)</td></tr>\n";
  print F "</table><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Transmitter Site RF Safety</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>General</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Occupational</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Maximum Permissible Exposure</b></td><td><font color=\"blue\">$std1</font> mW/cm<sup>2</sup></td><td><font color=\"blue\">$std2</font> mW/cm<sup>2</sup></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Distance to RF Safety Compliance</b></td><td><font color=\"blue\">$dx1_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$dx1_m</font> meters)</td><td><font color=\"blue\">$dx2_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$dx2_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\">(<a href=\"https://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet65/oet65.pdf\">FCC OET Bulletin 65</a>)&nbsp;&nbsp;<b>Estimated RF Power Density</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$rf_safe_pwrdens</font> mW/cm<sup>2</sup>&nbsp;&nbsp;&nbsp;&nbsp;(Directly Below the Radiating Antenna)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Total RF Input Power to the Antenna</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$tx_ant_input</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$tx_ant_input_mw</font> mW)</td></tr>\n";
  print F "<tr><td align=\"right\">(<a href=\"https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/subject-group-ECFR2f2e5828339709e/section-15.247\">FCC Part 15.247</a>)&nbsp;&nbsp;<b>Allowed RF Input Power to Antenna</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_ant_pwr</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$max_ant_pwr_mw</font> mW)</td></tr>\n";
  print F "<tr><td align=\"right\">(<a href=\"https://www.ecfr.gov/current/title-47/chapter-I/subchapter-C/part-74/subpart-F/section-74.644\">FCC Part 74.644</a>)&nbsp;&nbsp;<b>Maximum Allowable EIRP</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$fcc_eirp_dbm</font> dBm&nbsp;&nbsp;$fcc_check</td></tr>\n";
  print F "</table><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Terrain &amp; Atmospheric Conditions</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\" colspan=\"3\"><b><i>Specifications</i></b></td><tr>\n";
  if ($check3 eq "no") {
    print F "<tr><td align=\"right\"><b>Effective Earth Radius (K-Factor)</b></td><td colspan=\"2\"><font color=\"blue\">$k_str</font>&nbsp;&nbsp;(<font color=\"blue\">$k_dec</font> - $k_val)</td></tr>\n";
  }
  if ($check3 eq "yes") {
    print F "<tr><td align=\"right\"><b>Effective Earth Radius (K-Factor)</b></td><td colspan=\"2\"><font color=\"blue\">$k_str</font>&nbsp;&nbsp;($k_val)&nbsp;&nbsp;&nbsp;&nbsp;(Local Elevation: <font color=\"blue\">$k_ht_ft</font> feet / <font color=\"blue\">$k_ht_m</font> m)</td></tr>\n";
  }
  print F "<tr><td align=\"right\"><b>Grazing Angle</b></td><td colspan=\"2\"><font color=\"blue\">$graze_dg</font>&deg;&nbsp;&nbsp;(<font color=\"blue\">$graze_mr</font> milliradians)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Approximate Distance to Reflection Point</b></td><td colspan=\"2\"><font color=\"blue\">$grazing_dis_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$grazing_dis_km</font> kilometers)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Terrain Roughness (Supplied)</b></td><td colspan=\"2\"><font color=\"blue\">$rough_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rough_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Terrain Roughness (Calculated)</b></td><td colspan=\"2\"><font color=\"blue\">$rough_calc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rough_calc_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Average Annual Temperature</b></td><td colspan=\"2\"><font color=\"blue\">$temp_f</font>&deg; F&nbsp;&nbsp;(<font color=\"blue\">$temp_c</font>&deg; C)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Atmospheric Pressure (Sea Level Corrected)</b></td><td colspan=\"2\"><font color=\"blue\">$atmos_p</font> millibars</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Saturation Vapor Pressure</b></td><td colspan=\"2\"><font color=\"blue\">$es</font> millibars</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Partial Vapor Pressure</b></td><td colspan=\"2\"><font color=\"blue\">$vapor_p</font> millibars</td></tr>\n";
  printf F "<tr><td align=\"right\"><b>Ground Dielectric Constant</b></td><td colspan=\"2\"><font color=\"blue\">%.f</font></td></tr>\n", $diecon;
  printf F "<tr><td align=\"right\"><b>Ground Conductivity</b></td><td colspan=\"2\"><font color=\"blue\">%.3f</font> Siemens/meter</td></tr>\n", $earcon;
  print F "<tr><td align=\"right\"><b>Vigants-Barnett Climate Factor</b></td><td colspan=\"2\"><font color=\"blue\">$cli_vig</font>&nbsp;&nbsp;($cli_val)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Longley-Rice Climate Type</b></td><td colspan=\"2\"><font color=\"blue\">$climate</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Crane Rain Region</b></td><td colspan=\"2\"><font color=\"blue\">$region</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Local Area Humidity Type</b></td><td colspan=\"2\"><font color=\"blue\">$rough_hum</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Index of Surface Refraction</b></td><td colspan=\"2\"><font color=\"blue\">$nunits</font> N-units (parts per million)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Antenna Polarization</b></td><td colspan=\"2\"><font color=\"blue\">$polar</font></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Longley-Rice Situation Variability</b></td><td colspan=\"2\"><font color=\"blue\">$sit</font>% Confidence</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Longley-Rice Time Variability</b></td><td colspan=\"2\"><font color=\"blue\">$time</font>% Reliability</td></tr>\n";
  print F "</table><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Terrain Plotting Parameters</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Distance to the Radio Horizon</b></td><td><font color=\"blue\">$tx_rad_hor_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$tx_rad_hor_km</font> km)</td><td><font color=\"blue\">$rx_rad_hor_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$rx_rad_hor_km</font> km)</tr>\n";
  print F "<tr><td align=\"right\"><b>Path Minimum Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$min_elev_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$min_elev_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Path Average Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$avg_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$avg_ht_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Path Maximum Elevation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_elev_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$max_elev_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Earth Bulge at Path Midpoint</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$bulge_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$bulge_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Maximum Fresnel Zone Radius</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$max_fres_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$max_fres_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Additional Ground Clutter</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$gc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$gc_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Region for Terrain Plotting</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$city</font>, <font color=\"blue\">$state</font>&nbsp;&nbsp;(<font color=\"blue\">$country</font>)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Ideal Distance With These Antenna Heights</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$distance_max_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$distance_max_km</font> km)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Total Path Distance</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$dist_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$dist_km</font> km)</td></tr>\n";
  print F "</table><br><br><br><br><br><br><br><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Free-Space, ITM, Atmospheric, Rain, Misc. Losses</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Temperate Climate Foliage Loss</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$foli_ft</font> dB/foot&nbsp;&nbsp;(<font color=\"blue\">$foli_m</font> dB/meter)&nbsp;&nbsp;(Dense, Dry, In-Leaf)</td></tr>\n";
  print F "<tr><td align=\"right\">(Rain Rate: <font color=\"blue\">$rate</font> mm/hr)&nbsp;&nbsp;<b>Crane Rain Model Attenuation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$crane_rain_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$crane_rain_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$crane_rain_att_km</font> dB/km)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>NASA Simplified Rain Model Attenuation</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$nasa_rain_att_total</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Effective Rain Path Distance</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$rain_eff_mi</font> miles&nbsp;&nbsp;(<font color=\"blue\">$rain_eff_km</font> km)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Estimated Attenuation Due to Water Vapor</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$water_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$water_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$water_att_km</font> dB/km)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Estimated Attenuation Due to Oxygen Loss</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$oxy_att_total</font> dB&nbsp;&nbsp;(<font color=\"blue\">$oxy_att_mi</font> dB/mile)&nbsp;&nbsp;(<font color=\"blue\">$oxy_att_km</font> dB/km)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Miscellaneous Path Losses</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$tx_misc_loss</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#7EBDE5\"><b><i>Ideal vs. Realistic Expectations</i></b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Friis Free-Space Path Loss</b></td><td><font color=\"blue\">$fs</font> dB</td><td><font color=\"blue\">$fs_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>ITWOMv3 Primary Path Loss</b></td><td><font color=\"blue\">$itm</font> dB</td><td><font color=\"blue\">$itm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>ITWOMv3 Diversity Path Loss</b></td><td><font color=\"blue\">$div_itm</font> dB</td><td><font color=\"blue\">$div_itm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Total Atmospheric + Rain Path Losses</b></td><td><font color=\"blue\">$atmos_norain</font> dB</td><td><font color=\"blue\">$atmos_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Free-Space + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$fs_pl</font> dB</td><td><font color=\"blue\">$fs_pl_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>(Primary Path)&nbsp;&nbsp;ITWOMv3 + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$itm_pl</font> dB</td><td><font color=\"blue\">$itm_pl_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>(Diversity Path)&nbsp;&nbsp;ITWOMv3 + Atmospheric + Misc. Losses</b></td><td><font color=\"blue\">$div_itm_pl</font> dB</td><td><font color=\"blue\">$div_itm_pl_rain</font> dB</td></tr>\n";
  print F "</table><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"3\"><font size=\"4\"><b>Calculated Fade Margins</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$tx_name&nbsp;&nbsp;(TX)</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Receiver Threshold</b></td><td></td><td><font color=\"blue\">$BER_dbm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$BER_uvolt</font> &micro;V)&nbsp;&nbsp;&nbsp;&nbsp;($BER_crit)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Dispersive Fade Margin</b></td><td><td><font color=\"blue\">$dfm_fs</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>External Interference Fade Margin</b></td><td></td><td><font color=\"blue\">$eifm_fs</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Adjacent Channel Interference Fade Margin</b></td><td></td><td><font color=\"blue\">$aifm_fs</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Minimum Composite Fade Margin for This Climate</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$min_fade</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Potential Upfade</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$upfade</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Path Mean Time Delay</b></td><td align=\"center\" colspan=\"2\"><font color=\"blue\">$time_delay</font> nanoseconds</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#7EBDE5\"><b><i>Unfaded Values</i></b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td><td align=\"center\" bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Free-Space Loss Received Signal Level</b></td><td><font color=\"blue\">$rx_pwr</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_pwr_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_rain_uvolt</font> &micro;V)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Free-Space Thermal Fade Margin</b></td><td><font color=\"$tfm_color\">$tfm</font> dB</td><td><font color=\"$tfm_color_rain\">$tfm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>ITWOMv3 Loss Received Signal Level</b></td><td><font color=\"blue\">$rx_pwr_itm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_itm_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_pwr_itm_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_pwr_itm_rain_uvolt</font> &micro;V)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>ITWOMv3 Thermal Fade Margin</b></td><td><font color=\"$tfm_itm_color\">$tfm_itm</font> dB</td><td><font color=\"$tfm_itm_color_rain\">$tfm_itm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Space Diversity ITWOMv3 Received Signal Level</b></td><td><font color=\"blue\">$rx_div_pwr_itm</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_div_pwr_itm_uvolt</font> &micro;V)</td><td><font color=\"blue\">$rx_div_pwr_itm_rain</font> dBm&nbsp;&nbsp;(<font color=\"blue\">$rx_div_pwr_itm_rain_uvolt</font> &micro;V)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Space Diversity ITWOMv3 Thermal Fade Margin</b></td><td><font color=\"$div_tfm_color\">$div_tfm_itm</font> dB</td><td><font color=\"$div_tfm_color_rain\">$div_tfm_itm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Free-Space Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_fs_color\">$cmp_fs</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_fs_rain_color\">$cmp_fs_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Non-Diverstiy ITWOMv3 Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_itm_color\">$cmp_itm</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_itm_rain_color\">$cmp_itm_rain</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Space Diversity ITWOMv3 Loss Composite Fade Margin</b></td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_div_itm_color\">$cmp_div_itm</font> dB</td><td bgcolor=\"#CCCCBB\"><font color=\"$cmp_div_itm_rain_color\">$cmp_div_itm_rain</font> dB\</td></tr>\n";
  print F "</table><br><br><br><br><br><br><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"4\"><b>Vertical Space Diversity Antenna Parameters</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>$rx_name&nbsp;&nbsp;(RX-DIV)</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>Local Ground Elevation (AMSL)</b></td><td><font color=\"blue\">$rx_elv_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$rx_elv_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>User Supplied Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_m</font> meters)&nbsp;&nbsp;&nbsp;&nbsp;$div_ft_check</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Adjusted Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_calc_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_calc_m</font> meters)&nbsp;&nbsp;&nbsp;&nbsp;(Odd Multiple 1/2 wav.)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Calculated Ideal Spacing for Diversity Antenna</b></td><td><font color=\"blue\">$div_space_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_space_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Diversity Antenna Height (AGL)</b></td><td><font color=\"blue\">$div_ant_ht_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_ant_ht_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Overall Diversity Receiver Antenna Height (AMSL)</b></td><td><font color=\"blue\">$div_rx_ant_ht_ov_ft</font> feet&nbsp;&nbsp;(<font color=\"blue\">$div_rx_ant_ht_ov_m</font> meters)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Diversity Antenna Gain</b></td><td><font color=\"blue\">$div_ant_dbi</font> dBi&nbsp;&nbsp;(<font color=\"blue\">$div_ant_dbd</font> dBd)&nbsp;&nbsp;(Radome Loss: <font color=\"blue\">$rx_div_ant_gain_radome</font> dB)&nbsp;&nbsp;$div_gain_check</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Diversity Antenna Mechanical Tilt</b></td><td><font color=\"blue\">$tilt_rtd</font>&deg; to TX</td></tr>\n";
  print F "</table><br><br>\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"4\"><b>Target Outage Objectives &amp; Probabilities</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Specifications</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Outage Objective</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Reliability</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Required Composite Fade Margin</b></td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Bell System Short-Haul</b></td><td><font color=\"blue\">$obj_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj_nodiv_fs_cfm</font> dB</td></tr>\n";   
  print F "<tr><td align=\"right\"><b>One-Way Bell System Long-Haul</b></td><td><font color=\"blue\">$obj1_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj1_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj1_nodiv_fs_cfm</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way ITU-R High-Grade</b></td><td><font color=\"blue\">$obj2_nodiv_fs</font> SES/year</td><td><font color=\"blue\">$obj2_nodiv_fs_per</font>%</td><td><font color=\"blue\">$obj2_nodiv_fs_cfm</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way Bell System Short-Haul</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj_nodiv_fs_cfm_two</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way Bell System Long-Haul</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj1_nodiv_fs_cfm_two</font> dB</td></tr>\n";
  print F "<tr><td align=\"right\" bgcolor=\"#CCCCBB\"><b>Two-Way ITU-R High-Grade</b></td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_two</font> SES/year</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_per_two</font>%</td><td bgcolor=\"#CCCCBB\"><font color=\"blue\">$obj2_nodiv_fs_cfm_two</font> dB</td></tr>\n";
  print F "</table><br><br></font></body></html>\n";
close F;

open(F, ">", "index3.html") or die "Can't open index3.html: $!\n" ;
  print F "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
  print F "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
  print F "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
  print F "<font face=\"Helvetica\"><font size=\"-1\">\n";
  print F "<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\" width=\"100%\">\n";
  print F "<tr><td align=\"center\" bgcolor=\"#3498DB\" colspan=\"4\"><font size=\"5\"><b>Calculated Outage Objectives &amp; Probabilities</b></font></td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Without Spaced Vertical Antenna Diversity (Vigants/Free-Space)</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_nodiv_fs_yr</font> SES/year</td><td><font color=\"blue\">$SES_nodiv_fs_yr_rain</font> SES/year</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_nodiv_fs_per</font>%</td><td><font color=\"blue\">$SES_nodiv_fs_per_rain</font>%</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_nodiv_fs_yr</font>&nbsp;&nbsp;$worst_nodiv_fs_yr_val</td><td><font color=\"blue\">$worst_nodiv_fs_yr_rain</font>&nbsp;&nbsp;$worst_nodiv_fs_yr_val_rain</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Amplitude Dispersion Fading Outage</b></td><td><font color=\"blue\">$worst_amp_fade_fs</font> $worst_amp_fade_fs_val</td><td><font color=\"blue\">$worst_amp_fade_fs_rain</font> $worst_amp_fade_fs_val</td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>Without Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_nodiv_itm_yr</font> SES/year</td><td><font color=\"blue\">$SES_nodiv_itm_yr_rain</font> SES/year</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_nodiv_itm_per</font>%</td><td><font color=\"blue\">$SES_nodiv_itm_per_rain</font>%</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_nodiv_itm_yr</font>&nbsp;&nbsp;$worst_nodiv_itm_yr_val</td><td><font color=\"blue\">$worst_nodiv_itm_yr_rain</font>&nbsp;&nbsp;$worst_nodiv_itm_yr_val_rain</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Amplitude Dispersion Fading Outage</b></td><td><font color=\"blue\">$worst_amp_fade</font> $worst_amp_fade_val</td><td><font color=\"blue\">$worst_amp_fade_rain</font> $worst_amp_fade_rain_val</td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Spaced Vertical Antenna Diversity (Vigants/ITWOMv3)</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
  print F "<tr><td align=\"right\"><b>Space Diversity Improvement Factor</b></td><td><font color=\"$Isd_color\">$Isd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$Isd_itm_db</font> dB)&nbsp;&nbsp;&nbsp;&nbsp;$Isd_message_itm</td><td><font color=\"$Isd_color_rain\">$Isd_itm_rain</font>&nbsp;&nbsp;&nbsp;&nbsp;(<font color=\"blue\">$Isd_itm_db_rain</font> dB)&nbsp;&nbsp;&nbsp;&nbsp;$Isd_message_itm_rain</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_div_itm_yr</font> SES/year</td><td><font color=\"blue\">$SES_div_itm_yr_rain</font> SES/year</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_div_itm_per</font>%</td><td><font color=\"blue\">$SES_div_itm_per_rain</font>%</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_div_itm_yr</font>&nbsp;&nbsp;$worst_div_itm_yr_val</td><td><font color=\"blue\">$worst_div_itm_yr_rain</font>&nbsp;&nbsp;$worst_div_itm_yr_val_rain</td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Frequency Diversity (Vigants/ITWOMv3)</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
  print F "<tr><td align=\"right\"><b>Diversity Frequency</b></td><td colspan=\"2\"><font color=\"blue\">$frq_ghz_div</font> GHz&nbsp;&nbsp;&nbsp;&nbsp;(&Delta;F: <font color=\"blue\">$df_mhz</font> MHz)</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Frequency Diversity Improvement Factor</b></td><td><font color=\"$Ifd_color\">$Ifd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ifd_message_itm</td><td><font color=\"$Ifd_color_rain\">$Ifd_itm_rain</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ifd_message_itm_rain</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_frq_div_yr_itm</font> SES/year</td><td><font color=\"blue\">$SES_frq_div_yr_itm_rain</font> SES/year</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_frq_div_itm_per</font>%</td><td><font color=\"blue\">$SES_frq_div_itm_per_rain</font>%</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_frq_div_mo_itm</font>&nbsp;&nbsp;$worst_frq_div_mo_itm_val</td><td><font color=\"blue\">$worst_frq_div_mo_itm_rain</font>&nbsp;&nbsp;$worst_frq_div_mo_itm_val_rain</td></tr>\n";
  print F "<tr><td bgcolor=\"#7EBDE5\"><b><i>With Hybrid Diversity (Vigants/ITWOMv3)</i></b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>Without Rain Loss</b></td>\n";
  print F "<td bgcolor=\"#7EBDE5\"><b>With Rain Loss (Crane)</b></td><tr>\n";
  print F "<tr><td align=\"right\"><b>Hybrid (Space + Frequency) Diversity Improvement Factor</b></td><td><font color=\"$Ihd_color\">$Ihd_itm</font>&nbsp;&nbsp;&nbsp;&nbsp;$Ihd_message</td><td>&nbsp;</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Probability of Outage</b></td><td><font color=\"blue\">$SES_hyb_div_yr_itm</font> SES/year</td><td>&nbsp;</td></tr>\n";
  print F "<tr><td align=\"right\"><b>One-Way Multipath Reliability</b></td><td><font color=\"blue\">$SES_hyb_div_itm_per</font>%</td><td>&nbsp;</td></tr>\n";
  print F "<tr><td align=\"right\"><b>Annual Multipath Severely Errored Seconds</b></td><td><font color=\"blue\">$worst_hyb_div_yr_itm</font>&nbsp;&nbsp;$worst_hyb_div_yr_itm_val</td><td>&nbsp;</td></tr>\n";
  print F "</table><br><br></font></body></html>\n";
close F;

open(F, ">", "index4.html") or die "Can't open index4.html: $!\n" ;
  print F "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
  print F "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
  print F "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
  print F "<font face=\"Helvetica\"><font size=\"-1\">\n";
  print F "<center><table border=\"2\" cellpadding=\"8\"><tr><td colspan=\"10\" bgcolor=\"#7EBDE5\" align=\"center\"><font size=\"4\"><b>Terrain Analysis Reports</b></font></td></tr></table></center><br>\n";
  print F "<pre><font color=\"maroon\"><b>HAAT Calculation</b></font>\n\n";

  open(F1, "<", "$tx_name-site_report.txt") or die "Can't open file $tx_name-site_report.txt: $!\n";
    while (<F1>) {
      chomp;
      print F "$_\n";
    }
  close F1;

  print F "\n<font color=\"maroon\"><b>HAAT Calculation</b></font>\n\n";

  open(F1, "<", "$rx_name-site_report.txt") or die "Can't open file $rx_name-site_report.txt: $!\n";
    while (<F1>) {
      chomp;
      print F "$_\n";
   }
  close F1;

  if ($do_div eq "yes") {
    print F "<font color=\"maroon\"><b>HAAT Calculation</b></font>\n\n";

    open(F1, "<", "$rx_div_name-site_report.txt") or die "Can't open file $rx_div_name-site_report.txt: $!\n";
      while (<F1>) {
        chomp;
        print F "$_\n";
      }
    close F1;
  }

  print F "\n<font color=\"maroon\"><b>SPLAT! Path Profile Calculations</b></font>\n\n";

  $found = 0;
  open(F1, "<", "$rx_name-to-$tx_name.txt") or die "Can't open file $rx_name-to-$tx_name.txt: $!\n";
    while ($line = <F1>) {
      chomp $line;
      if ($line =~ /Site Name/) {
        $found = 1;
      }
      if ($found) {
        print F "$line\n";
      }
    }
  close F1;

  if ($do_div eq "yes") {
    print F "\n<font color=\"maroon\"><b>SPLAT! Path Profile Calculations</b></font>\n\n";

    $found = 0;
    open(F1, "<", "$rx_div_name-to-$tx_name.txt") or die "Can't open file $rx_div_name-to-$tx_name.txt: $!\n";
      while ($line = <F1>) {
        chomp $line;
        if ($line =~ /Site Name/) {
          $found = 1;
        }
        if ($found) {
          print F "$line\n";
        }
      }
    close F1;
  }

  print F "\n<font color=\"maroon\"><b>SPLAT! Path Profile Calculations</b></font>\n\n";

  $found = 0;
  open(F1, "<", "$tx_name-to-$rx_name.txt") or die "Can't open file $tx_name-to-$rx_name.txt: $!\n";
    while ($line = <F1>) {
      chomp $line;
      if ($line =~ /Site Name/) {
        $found = 1;
      }
      if ($found) {
        print F "$line\n";
      }
    }
  close F1;

  print F "</pre></body></html>\n"; 
close F;

open(F, ">", "index5.html") or die "Can't open index5.html: $!\n" ;
  print F "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">\n";
  print F "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"></head>\n";
  print F "<body bgcolor=\"#D3D3D3\" text=\"#000000\" link=\"blue\">\n";
  print F "<font face=\"Helvetica\"><font size=\"-1\">\n";
  print F "<center>\n";
  print F "<p><img src=\"TopoMap.png\" height=\"480\" width=\"640\"><br><b>General Coverage Topographical Map<br>$country ($city, $state)</b></p>\n";
  if ($do_div eq "no") {
    print F "<p><img src=\"LOSMap.png\" height=\"480\" width=\"640\"><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_name</font></b></p>\n";
  }
  elsif ($do_div eq "yes") {
  print F "<p><img src=\"LOSMap.png\" height=\"480\" width=\"640\"><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_name</font></b></p>\n";
  print F "<p><img src=\"LOSMap-div.png\" height=\"480\" width=\"640\"><br><b>Approximate Line-of Sight Radio Coverage with a $tx_ant_ht_ft ft Receive Antenna Height<br><font color=\"#00FF00\">$tx_name</font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#00FFFF\">$rx_div_name </font>&nbsp;&nbsp;&nbsp;&nbsp;<font color=\"#FFFF00\">$tx_name+$rx_div_name</font></b></p>\n";
  }
  print F "<p><img src=\"LossMap1.png\" height=\"480\" width=\"640\"><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $tx_name</b></p>\n";
  if ($do_div eq "no") {
    print F "<p><img src=\"LossMap2.png\" height=\"480\" width=\"640\"><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_name</b></p>\n";
  }
  elsif ($do_div eq "yes") {
    print F "<p><img src=\"LossMap2.png\" height=\"480\" width=\"640\"><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_name</b></p>\n";
    print F "<p><img src=\"LossMap-div.png\" height=\"480\" width=\"640\"><br><b>Approximate Omnidirectional ITM Path Loss Coverage at $rx_div_name</b></p>\n";
  }
  print F "<br><br><font size=\"-1\"><a href=\"http://www.gbppr.net\">GBPPR RadLab</a> $ver</font><br><font color=\"red\"><b>EXPERIMENTAL</b></font>\n";
  print F "<br><br><font size=\"-1\">These calculations are only estimates based on the provided data.<br>There is no guarantee that a microwave link is possible, even if it \"looks\" O.K.<br>This is mostly just for fun and I have no idea if it's accurate.</font>\n";
  print F "</center></font></body></html>\n";
close F;

## Make PDF output
#
$ENV{HTMLDOC_NOCGI}=1;
&System($args = "$htmldoc --links --header ... --linkcolor blue --linkstyle plain --left 0.25in --footer ..1 --quiet --webpage -f $outpdf index1.html index2.html index3.html index4.html index5.html");

## Done
#
if ($DEBUG == 1) {
  unlink "curvature.gp", "elev1", "elev.gp", "fresnel.gp", "fresnel_pt_6.gp", "loss.png";
  unlink "loss-profile.gp", "profile2.gp", "profile.gp", "pro.png", "reference.gp";
  unlink "rx.lrp", "rx.qth", "RX-site_report.txt", "RX-to-TX.txt", "splat2.gp";
  unlink "splat3.gp", "splat.gp", "tx.lcf", "tx.lrp", "tx.qth", "TX-site_report.txt";
}

exit 0;
