/**
 * Returns the currently authenticated user's information derived from the verified token.
 */
export const getMe = async (req, res) => {
  return res.status(200).json({
    user: {
      id: req.user.id,
      email: req.user.email,
      userMetadata: req.user.userMetadata,
      appMetadata: req.user.appMetadata,
    },
  });
};

