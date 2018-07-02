import numpy as np

def accuracy(predictions, labels):
  return (100.0 * np.sum(predictions ==labels)
          / predictions.shape[0])

class LossFunction:
    def calc_loss_and_grad_for_batch(self, X, y):
        pass

    def get_params_as_matrix(self):
        pass

    def update_params(self):
        pass


class LonelySoftmaxWithReg(LossFunction):
    def __init__(self, dim=None, num_labels=None, reg_param=None):
        self.W = np.random.randn(dim, num_labels)*np.sqrt(2/(dim+1))
        self.b = np.zeros([1, num_labels], dtype=np.double)
        self.reg = reg_param

    def calc_loss_and_grad_for_batch(self, X, y):
        return FunctionsBoxes.softmax_loss_and_gradient_regularized(self.get_params_as_matrix(),self.add_bias_dimension(X), y, self.reg)

    def get_params_as_matrix(self):
        return np.vstack((self.W, self.b))

    def add_bias_dimension(self, X):
        return np.column_stack((X, np.ones(X.shape[0])))

    def predict(self, X):
        return np.argmax(self.add_bias_dimension(X).dot(self.get_params_as_matrix()), axis=1)

    def update_params(self, params):
        self.b = params[-1]
        self.W = params[0:-1]


class FunctionsBoxes:

    @staticmethod
    def softmax_loss_and_gradient_regularized(W, X, y, reg):
        """
        Softmax loss function, with quadratic regularization

        Inputs and outputs are the same as softmax_loss_naive.
        """
        loss = 0.0

        num_classes = W.shape[1]
        num_train = X.shape[0]
        dW = np.zeros_like(W)

        scores = X.dot(W)
        scores_exp = np.exp(scores)

        numerical_stab_factors = np.max(scores, axis=1)
        normalized_scores = np.exp(scores.T - numerical_stab_factors.T).T
        scores_sums = np.sum(normalized_scores, axis=1)
        total_scores_mat = (normalized_scores.T / scores_sums.T).T
        labels_mat = np.zeros_like(scores)
        labels_mat[np.arange(0, num_train), y] = 1
        dW += (X.T).dot(total_scores_mat - labels_mat)
        dW /= num_train
        dW += (2 * reg) * W

        class_scores = normalized_scores[np.arange(len(scores_exp)), y.T]
        loss = np.sum(np.log(scores_sums) + np.log(np.ones(num_train) / class_scores))
        loss /= num_train
        loss += reg * np.sum(W * W)

        return loss, dW


def train_with_sgd(loss_function, t_data, t_labels, max_iter, learning_rate, decay_rate,
                   batch_size, convergence_criteria, gamma ,v_data, v_labels):
    """
    We assume that the function can receive dynamic data size
    :param loss_function:
    :param t_data: The data set (ideally should be loaded to RAM on demand)
    :param t_labels: The corresponding labels
    :param max_iter:
    :param learning_rate:
    :param decay_rate:
    :param batch_size:
    :return:
    """
    m = np.zeros(loss_function.get_params_as_matrix().shape, dtype=np.double)
    loss_history = []
    accuracy_history = {"test_set": [],
                        "validation_set": []
                        }
    cur_learning_rate = learning_rate
    num_train, dim = t_data.shape
    num_of_batches = int(np.ceil(num_train / batch_size))
    cur_loss = 0.0
    for i in range(0, max_iter):
        x_batch = None
        y_batch = None

        cur_learning_rate = update_learning_rate_step(learning_rate, 10, i, decay_rate)

        assert len(t_data) == len(t_labels)
        p = np.random.permutation(num_train)
        t_data = t_data[p]
        t_labels = t_labels[p]
        for j in range(0, num_of_batches):
            x_batch = t_data[j * batch_size:(j + 1) * batch_size]
            y_batch = t_labels[j * batch_size:(j + 1) * batch_size]

            cur_loss, grad = loss_function.calc_loss_and_grad_for_batch(x_batch, y_batch)
            prev_params = loss_function.get_params_as_matrix()

            # Parameter update, change mto momentum\adaGrad

            #updated_params = prev_params-learning_rate*grad

            # Momentum update
            m = gamma * m + cur_learning_rate*grad
            updated_params = prev_params - m

            loss_function.update_params(updated_params)
            loss_history.append(cur_loss)

        test_set_accuracy = accuracy(loss_function.predict(t_data), t_labels)
        validation_set_accuracy = accuracy(loss_function.predict(v_data), v_labels)

        print("After %d epochs, train set accuracy is %d" % (i+1, test_set_accuracy))
        print("After %d epochs, validation set accuracy is %d" % (i+1, validation_set_accuracy))

        accuracy_history['test_set'].append(test_set_accuracy)
        accuracy_history['validation_set'].append(validation_set_accuracy)

        #if np.abs(loss_history[-1]-loss_history[-2]) < convergence_criteria:
        #    break

    return loss_history, accuracy_history


def update_learning_rate_simple(learning_rate, decay_rate, iteration):
    if iteration < 100:
        return 0.01
    else:
        return 0.001


def update_learning_rate_step(initial_learning_rate, interval, iteration, drop_rate):
    return initial_learning_rate * np.power(drop_rate,
                                     np.floor((1 + iteration) / interval))

