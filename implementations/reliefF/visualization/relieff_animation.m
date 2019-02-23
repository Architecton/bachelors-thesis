function [weights] = relieff_animation(data, m, k, dist_func, timeout, use_deletions)
	% function [weights] = relieff_animation(data, m, k, dist_func, timeout, use_deletions)
	%
	% Create an animation of the ReliefF feature selection algorithm
	% using three dimensional feature space.
	%
	% data --- matrix of training data with class column as the last column.
	% m --- the m parameter (example sample size)
	% k --- number of examples from each class to take
	% dist_func --- distance function for evaluating distance between
	% examples. The function should be able to take two matrices of
	% examples and return a vector of distances between the examples.
	% use_deletions --- logical value that specifies whether to delete the
	% computation visualization when moving onto next example in the
	% sample.
	
	% Use deletions and default timeout if corresponding parameter not specified.
	if nargin < 5
		use_deletions = 1;
		timeout = 0.3;
	end

	% diff: score distance between two examples
	function [res] = diff(idx_feature, e1, e2, max_f_val, min_f_val)
		% if feature continuous
		% TODO continuous? optional argument.
		if 1
			res = abs(e1(:, idx_feature) - e2(:, idx_feature))./(max_f_val - min_f_val);
		else  % if feature discrete
			if e1(idx_feature) == e2(idx_feature); res = 0; else; res = 1; end
		end
	end

	% Create scatter plot of data
	figure(1); hold on;
	scatter3(data(:, 1), data(:, 2), data(:, 3), 30, categorical(data(:, 4)), 'filled');
	xlabel('a'); ylabel('b'); zlabel('c'); view(30, 50); grid on;
	pause on


	weights = zeros(1, size(data, 2) - 1);  % Initialize weights.
	idx_sampled = randsample(1:size(data, 1), m); % Get index of elements in sample.
	
	% Compute minimum and maximum feature values.
	max_f_vals = max(data(:, 1:end-1));
	min_f_vals = min(data(:, 1:end-1));
	
	% Get unique classes and their probabilities.
	classes = unique(data(:, end));
	p_classes = [classes, histcounts(data(:, end), 'Normalization', 'probability')'];
	
	% Go over examples in sample.
	for idx = idx_sampled
		
		% ### PLOTTING ###
		% Display current weight values.
		hT = title({'ReliefF Algorithm Visualization', sprintf('$$ weights = [%.3f, %.3f, %.3f] $$', weights(1), weights(2), weights(3))},'interpreter','latex');
		set(hT, 'FontSize', 17);
		% ### /PLOTTING ###
		
		
		
		% Get next sampled example.
		e = data(idx, :);
		
		
		
		% ### PLOTTING ###
		% Mark selected example.
		sample_p = plot3(e(1), e(2), e(3), 'ro', 'MarkerSize', 10);
		pause(timeout);
		% ### /PLOTTING ###
		
		
		
		% Get index of sampled example in group of examples of same class.
		data_class_aux = data(1:idx-1, end); idx_class = idx - sum(data_class_aux ~= e(end));
		
		% Find k nearest examples from same class.
		distances_same = dist_func(repmat(e(1:end-1), sum(data(:, end) == e(end)), 1), data(data(:, end) == e(end), 1:end-1));
		distances_same(idx_class) = inf;
		[~, idxs_closest_same] = mink(distances_same, k);
		data_same_aux = data(data(:, end) == e(end), :);
		closest_same = data_same_aux(idxs_closest_same, :);
		
		
		% ### TODO ###
		% Can remove leading class column as order follows the classes
		% vector.
		
		% Allocate matrix template for getting nearest examples from other
		% classes.
		classes_vect = repmat(classes(classes ~= e(end)), 1, k)'; classes_vect = classes_vect(:);
		closest_other = [classes_vect, zeros(k * (length(classes) - 1), size(data, 2))];
		top_ptr = 1;  % Initialize pointer for adding examples to template matrix.
		for cl = classes'  % Go over classes different than the one of current sampled example.
			if cl ~= e(end)
				% Get closest k examples with class cl
				distances_cl = dist_func(repmat(e(1:end-1),  sum(data(:, end) == cl), 1), data(data(:, end) == cl, 1:end-1));
				[~, idx_closest_cl] = mink(distances_cl, k);
				% Add found closest examples to matrix.
				data_cl_aux = data(data(:, end) == cl, :);
				closest_other(top_ptr:top_ptr+k-1, 2:end) = data_cl_aux(idx_closest_cl, :);
				top_ptr = top_ptr + k;
			end
		end
		
		
		
		% ### PLOTTING ###
		% Plot distances to closest examples from same class and closest examples from other classes.
		line_ctr = 1;
		lines_closest_same = cell(1, k);
		for closest_same_nxt = closest_same(:, 1:end-1)'
			lines_closest_same{line_ctr} = plot3([e(1), closest_same_nxt(1)], [e(2), closest_same_nxt(2)], [e(3), closest_same_nxt(3)], 'g-', 'LineWidth', 4);
			pause(timeout);
			line_ctr = line_ctr + 1;
		end
		pause(timeout);
		
		line_ctr = 1;
		lines_closest_other = cell(1, k);
		for closest_other_nxt = closest_other(:, 2:end-1)'
			lines_closest_other{line_ctr} = plot3([e(1), closest_other_nxt(1)], [e(2), closest_other_nxt(2)], [e(3), closest_other_nxt(3)], 'r-', 'LineWidth', 4);
			pause(timeout);
			line_ctr = line_ctr + 1;
		end
		
		if use_deletions
			delete(sample_p); cellfun(@delete, lines_closest_same); cellfun(@delete, lines_closest_other);
		end
		% ### /PLOTTING ###
		
		
		
		
		% Get probabilities of classes not equal to class of sampled example.
		p_classes_other = p_classes(p_classes(:, 1) ~= e(end), 2);
		
		% Compute diff sum weights for closest examples from different class.
		weights1 = p_classes_other./(1 - p_classes(p_classes(:, 1) == e(end), 2));
		
		% Go over features.
		for t = 1:size(data, 2) - 1
			% Update feature weights.
			sum1 = sum(diff(t, repmat(e(1:end-1), k, 1), closest_same(:, 1:end-1), max_f_vals(t), min_f_vals(t))./(m*k));
			sum2 = movsum(diff(t, repmat(e(1:end-1), k*(length(classes)-1), 1), closest_other(:, 2:end-1), max_f_vals(t), min_f_vals(t)), k);
			sum2 = sum2(2:k:end);
			sum3 = sum(weights1 .* sum2)./(m*k);
			weights(t) = weights(t) - sum1 + sum3;
		end
	end
end