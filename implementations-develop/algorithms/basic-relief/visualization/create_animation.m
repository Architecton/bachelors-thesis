% Test data 1
data1 = [0 0 0 0; 0 0 1 0; 0 1 1 1; 0 1 0 1; 1 0 0 1; 1 0 1 1; 1 1 0 0; 1 1 0 0];

% Test data 2
data2 = load('rba_test_data.m');

% Test data 3
data3 = load('rba_test_data2.m');

% Set m parameter.
m = 50;

% Use deletions
use_deletions = 1;

% Set example animation timeout
timeout = 0.1;

% Create animation and display final feature weights.
[rank, weights] = relief_animation(data3, size(data3, 1),  @(a, b) minkowski_dist(a, b, 2), 0, timeout, use_deletions);
fprintf('weights = [%.3f, %.3f, %.3f]\n', weights);

% Define minkowski function that takes two vectors or matrices
% and the parameter p and returns the distance or vector of distances
% between the examples.
function d = minkowski_dist(a, b, p)
	d = sum(abs(a - b).^p, 2).^(1/p);
end
