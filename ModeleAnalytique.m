%% données
clear all; close all; clc;


data = csvread('1209-2609_trafictot.csv',1);
hours = data(:,1);
ped = data(:, 2);
veh = data(:,3).*1.1;

bus = data(:,4);
sc = data(:,5);

%% représentativité swisscom = variable, représentativité compteurs = fixe

rep_vcomp= 0.8; %part de vehicules comptes sur tous les vehicules 
rep_bcomp = 0.8; %part des passagers de bus comptes sur tous les passagers
rep_pcomp = 0.4; %part des pietons comptes sur tous les pietons

solution =[];
trafic = [];
fval =[];
alphasc = [];

tic
for i = 1:length(ped) 
totcompt = ped(i) + veh(i) +bus(i);
part_pcomp = ped(i) / totcompt;
part_vcomp = veh(i) / totcompt;
part_bcomp = bus(i) /totcompt;


f = @(x) (x(1) - sc(i)/x(5)).^2;

x0 = [totcompt;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0;0];

%contraintes lin?aires
A = -1 * eye(length(x0));
b = zeros(length(x0),1); % toutes les variables positives
 
Aeq = [1 -1 -1 -1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
     0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
     0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
     0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0;
     0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0; 
     0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0 0 0 0;
     0 0 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 0;
     0 0 0 0 0 0 0 0 sc(i) 0 0 -1 0 0 0 0 0 0 0 0;
     0 0 0 0 0 0 0 0 0 sc(i) 0 0 -1 0 0 0 0 0 0 0;
     0 0 0 0 0 0 0 0 0 0 sc(i) 0 0 -1 0 0 0 0 0 0;
     0 0 0 0 0 0 0 0 0 0 0 -1 0 0 0 0 0 ped(i) 0 0;
     0 0 0 0 0 0 0 0 0 0 0 0 -1 0 0 0 0 0 veh(i) 0;
     0 0 0 0 0 0 0 0 0 0 0 0 0 -1 0 0 0 0 0 bus(i);
     
     ];
 
beq = [0;ped(i)/rep_pcomp;veh(i)/rep_vcomp;bus(i)/rep_bcomp;1;1; sc(i); 0;0;0;0;0;0]; 

%contraintes non lineaires

ceq = @(x) [(x(6)*x(1)-x(2));
        (x(7)*x(1)-x(3));
        (x(8)*x(1)-x(4));];
c = @(x) [(totcompt - x(1)*(rep_pcomp*x(6) + rep_vcomp*x(7) + rep_bcomp*x(8)));
        (x(5)*x(1) -sc(i));
        (x(16)*x(3)-x(13));
        (x(15)*x(2)-x(12));
        (x(17)*x(4) - x(14));
        ((x(15)*x(2) +x(16)*x(3) + x(17)*x(4))/(x(2)+x(3)+x(4)) - x(5));

        ];
    
fnonlin = @(x) deal(c(x), ceq(x));
 
lb = zeros(length(x0),1); %lower bound
ub = [Inf; Inf; Inf; Inf; 1; 1; 1; 1; 1; 1; 1; Inf; Inf; Inf; 1; 1; 1; Inf;Inf;Inf]; %upperbound

x = fmincon(f,x0,A,b, Aeq, beq, lb, ub, fnonlin);
solution = [solution x];
fval = [fval f(x)];
 
end

toc
csvwrite('solution.csv', solution);

