# author: Mckenna Cisler <mckenna_cisler@brown.edu>
# purpose: to generate a polar sky plot of received packets, 
# based on data from packet-rx-az-el-rssi.py

ladd_d = csvread("data/rx-az-el-rssi_ladd.csv",1,6);
rome_d = csvread("data/rx-az-el_rome.csv",1,6);

%figure;
%scatter(ladd_d(:,1), ladd_d(:,2), 'filled');

%figure;
%polarscatter(ladd_d(:,1), 90-ladd_d(:,2), 'filled'); % 12*abs(ladd_d(:,3)),
%title("Ladd Azimuth vs. Elevation vs. Doppler Magnitude");
%ax = gca;
%ax.ThetaZeroLocation = 'top';

figure;
min_rssi = -120
rssi = ladd_d(:,4); 
rssi(rssi == 0) = min_rssi;
-min_rssi+rssi
polarscatter(ladd_d(:,1), 90-ladd_d(:,2), 5*(-min_rssi+rssi+1), 'filled');
title("Ladd Azimuth vs. Elevation vs. Packet RSSI");
ax = gca;
ax.ThetaZeroLocation = 'top';

%% remove first points
%rome_d_new = rome_d(79:end,:);
%
%figure;
%scatter(rome_d_new(:,1), rome_'filled', d_new(:,2), 'filled');
%
%figure;
%polarscatter(rome_d_new(:,1), 90-rome_d_new(:,2), 'filled'); %, 12*abs(rome_d_new(:,3))
%title("Rome Azimuth vs. Elevation vs. Doppler Magnitude");
%ax = gca;
%ax.ThetaZeroLocation = 'top';
