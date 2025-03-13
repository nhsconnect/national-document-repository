export type NdrTokenData = {
    exp: number;
    iss: string;
    smart_card_role: string;
    selected_organisation: {
        name: string;
        org_ods_code: string;
        role_code: string;
        is_BSOL: boolean;
    };
    repository_role: string;
    ndr_session_id: string;
    nhs_user_id: string;
};
