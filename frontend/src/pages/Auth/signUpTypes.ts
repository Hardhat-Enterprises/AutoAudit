export type SignUpFormData = {
  firstName: string;
  lastName: string;
  email: string;
  organizationName: string;
  password: string;
  confirmPassword: string;
}

export type SignUpSubmitPayload = SignUpFormData & {
  agreeTerms: boolean;
}
