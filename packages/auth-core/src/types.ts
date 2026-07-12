/** Venture tags per SG auth_surface_matrix_v1 identity plane. */
export type Venture = "sourcea" | "noetfield" | "trustfield";

/** Default member role; ops/partner extended per venture schema. */
export type Role = "member" | "partner" | "ops";

export type AppMetadata = {
  venture?: Venture;
  role?: Role;
};

export type AuthRoutePath =
  | "/auth/sign-in"
  | "/auth/sign-up"
  | "/auth/callback"
  | "/auth/sign-out";
