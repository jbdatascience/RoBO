"""
This module contains the probability of improvement acquisition function.

class:: PI(AcquisitionFunction)

    .. method:: __init__(model, X_lower, X_upper, par = 0.01, **kwargs)

        :param model: A model should have at least the function getCurrentBest()
                      and predict(X, Z).

    .. method:: __call__(x, Z=None, derivative=False, **kwargs)

        :param x: The point at which the function is to be evaluated. Its shape is (1,n), where n is the dimension of the search space.
        :type x: np.ndarray (1, n)
        :param Z: instance features to evaluate at. Can be None.
        :param par: A parameter meant to control the balance between exploration and exploitation of the acquisition
                    function. Empirical testing determines 0.01 to be a good value in most cases.
        :param derivative: Controls whether the derivative is calculated and returned.
        :type derivative: Boolean

        :returns:
"""



from scipy.stats import norm
import numpy as np
from robo import BayesianOptimizationError 
from robo.acquisition.base import AcquisitionFunction 
class PI(AcquisitionFunction):
    
    long_name = "Probability of Improvement" 
    def __init__(self, model, X_lower, X_upper, par=0.1, **kwargs):
        """

        :param model: A GPyModel contatining current data points.
        :param X_lower: Lower bounds for the search, its shape should be 1xn (n = dimension of search space)
        :type X_lower: np.ndarray (1,n)
        :param X_upper: Upper bounds for the search, its shape should be 1xn (n = dimension of search space)
        :type X_upper: np.ndarray (1,n)
        :param par: A parameter meant to control the balance between exploration and exploitation of the acquisition
                    function. Empirical testing determines 0.01 to be a good value in most cases.

        """
        self.model = model
        self.par = par
        self.X_lower = X_lower
        self.X_upper = X_upper

    def __call__(self, X, Z=None, derivative=False, **kwargs):
        """
        A call to the object returns the PI and derivative values.

        :param x: The point at which the function is to be evaluated.
        :type x: np.ndarray (1,n)
        :param Z: Instance features to evaluate at. Can be None.
        :param derivative: This controls whether the derivative is to be returned.
        :type derivative: Boolean
        :param kwargs:
        :return: The value of PI and its derivative at x.
        """
        if X.shape[0] > 1 :
            raise BayesianOptimizationError(BayesianOptimizationError.SINGLE_INPUT_ONLY, "PI is only for single x inputs")
        if np.any(X < self.X_lower) or np.any(X > self.X_upper):
            if derivative:
                f = 0
                df = np.zeros((1, X.shape[1]))
                return np.array([[f]]), np.array([df])
            else:
                return np.array([[0]])

        
        dim = X.shape[1]
        m, v = self.model.predict(X, Z)
        eta = self.model.getCurrentBest()
        s = np.sqrt(v)
        z = (eta - m - self.par) / s 
        f = norm.cdf(z)
        if derivative:
            dmdx, ds2dx = self.model.predictive_gradients(X)
            dmdx = dmdx[0]
            ds2dx = ds2dx[0][:, None]
            dsdx = ds2dx / (2 * s)
            df = (-(-norm.pdf(z) / s) * (dmdx + dsdx * z)).T
            
        if len(f.shape) == 1:
            return_f = np.array([f])
        if derivative:
            if len(df.shape) == 3:
                return_df = df
            else:
                return_df = np.array([df])
                
            return return_f, return_df
        else:
            return return_f
