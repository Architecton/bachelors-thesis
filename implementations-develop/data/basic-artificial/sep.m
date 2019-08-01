subplot(3, 1, 1)
scatter(rba_test_data2(:, 1), rba_test_data2(:, 2), 30, categorical(rba_test_data2(:, 4)), 'Filled')
xlabel('\nu_{1}', 'Interpreter', 'Tex')
ylabel('\nu_{2}', 'Interpreter', 'Tex')
title('Ločljivost razredov po atributih \nu_{1} in \nu_{2}', 'Interpreter', 'Tex')

subplot(3, 1, 2)
scatter(rba_test_data2(:, 1), rba_test_data2(:, 3), 30, categorical(rba_test_data2(:, 4)), 'Filled')
xlabel('\nu_{1}', 'Interpreter', 'Tex')
ylabel('\nu_{3}', 'Interpreter', 'Tex')
title('Ločljivost razredov po atributih \nu_{1} in \nu_{3}', 'Interpreter', 'Tex')

subplot(3, 1, 3)
scatter(rba_test_data2(:, 2), rba_test_data2(:, 3), 30, categorical(rba_test_data2(:, 4)), 'Filled')
xlabel('\nu_{2}', 'Interpreter', 'Tex')
ylabel('\nu_{3}', 'Interpreter', 'Tex')
title('Ločljivost razredov po atributih \nu_{2} in \nu_{3}', 'Interpreter', 'Tex')